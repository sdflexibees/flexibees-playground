import datetime
from functools import reduce
import math
import pandas as pd
import json
from apps.admin_app.views import api_logging
from apps.employer.constants import FLEXIFIT_INTERVIEW_CLEARED, FUNCTIONAL_INTERVIEW_CLEARED
from core.constants import EMPLOYER_LOGIN_DAYS
from core.response_format import message_response
import torch
from django.contrib.postgres.aggregates import ArrayAgg
from apps.admin_app.models import Domain, Skill
from rest_framework.response import Response
from apps.candidate.models import EmploymentDetail, Flexifit, FunctionalFeedback
from apps.common.constants import PENDING_STATUS
from apps.common.models import CustomSkill
from django.db.models import F
from sentence_transformers import SentenceTransformer, util
from apps.common.response_messages import something_went_wrong
from rest_framework import status
from core.response_format import message_response
from core.response_messages import invalid_input
from django.db.models import Q

# Determine the device cpu or gpu
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Load the BERT model (SentenceTransformer) with the 'paraphrase-multilingual-MiniLM-L12-v2' variant.
# The 'to(device)' part ensures that the model runs on the designated hardware (like a GPU, CPU) if available, 
st_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2').to(device)

def calculate_similarity_scores(job_skills):
    """
    This function calculates similarity scores between job skills and candidate skills
    using a BERT model to generate embeddings for the job skills and comparing them with 
    pre-generated candidate skill embeddings. The similarity scores are then returned as a dictionary.

    Parameters:
    job_skills (list): A list of job-related skills for which the similarity scores 
                    need to be calculated.

    Returns:
    dict: A dictionary with job skills as keys and corresponding similarity scores 
        with candidate skills as values.
        
        Sample Response Format:
        {
            'job_skill_1': {'candidate_skill_1': 0.85, 'candidate_skill_2': 0.76},
            'job_skill_2': {'candidate_skill_1': 0.92, 'candidate_skill_2': 0.67},
            ...
        }
    """

    # Initialize a list to collect log data, starting with the function call log
    log_data = [f"info|| {datetime.datetime.now()}: calculate similarity scores function"]

    try:
        # Step 1: Generate job skill embeddings and move them to the specified device (e.g., GPU, CPU)
        # `st_model.encode()` converts the list of job skills into embeddings (vectors)
        # `convert_to_tensor=True` ensures the embeddings are returned as a PyTorch tensor
        job_embeddings = st_model.encode(job_skills, convert_to_tensor=True).to(device)

        # Step 2: Handle candidate skill embeddings
        # Define file names for the candidate embeddings and the corresponding skills
        candidate_embeddings_file = 'candidate_embeddings.pt'
        candidate_skills_file = 'candidate_skills.json'

        try:
            # Load the candidate skills from a JSON file
            with open(candidate_skills_file, 'r') as json_file:
                candidate_skills = json.load(json_file)

            # Load the candidate embeddings from a PyTorch file and move them to the specified device
            candidate_embeddings = torch.load(candidate_embeddings_file).to(device)

        except FileNotFoundError:
            # If the files are not found, return a 404 response with an appropriate message
            return Response(message_response(something_went_wrong), status=status.HTTP_404_NOT_FOUND)

        # Step 3: Calculate similarity scores between candidate embeddings and job embeddings
        # `util.pytorch_cos_sim` computes the cosine similarity between the two sets of embeddings
        similarity_matrix = util.pytorch_cos_sim(candidate_embeddings, job_embeddings)

        # Step 4: Convert the similarity matrix to a pandas DataFrame for better visualization
        # - `similarity_matrix.cpu().numpy()` moves the tensor to the CPU and converts it to a NumPy array
        # - `pd.DataFrame()` creates a DataFrame where:
        #     - Columns represent job skills
        #     - Rows represent candidate skills
        df_similarity = pd.DataFrame(similarity_matrix.cpu().numpy(), columns=job_skills, index=candidate_skills)

        # Step 5: Convert the DataFrame to a dictionary and return it
        return df_similarity.to_dict()

    except Exception as e:
        # If any error occurs during the process, log the error message
        log_data.append(f"error || exception :{e}")
        log_data.append("LINE_BREAK")

        # Log the collected data (errors, information, etc.) to the API logging system
        api_logging(log_data)

        # Return a 400 response indicating invalid input, along with an appropriate message
        return Response(message_response(invalid_input), status=400)

def calculate_experience(experience_obj):
    """
    Calculate the number of years of experience between two dates.
    """
    end_date = experience_obj['end_date']
    if end_date is None:
        end_date = datetime.datetime.now().date()
    # Calculate the difference in years, months, and days
    delta = end_date - experience_obj['start_date']
    # Calculate the total number of years, including fractional years
    years_of_experience = delta.days / 365.25  # 365.25 accounts for leap years
    return years_of_experience

def get_job_required_hours(job):
    """
    Retrieves the required working hours per day for a given job.

    Parameters:
    job (object): An object representing a job with a `details` attribute.

    Returns:
    int or None: The number of required hours per day, or None if not applicable.
    """

    # Extract job type from job details
    job_type = job.details.get('job_type')

    # Return None if job type is not specified
    if not job_type:
        return None

    # Map job type descriptions to corresponding hours
    options = {
        "2-3 hours per day": 2,
        "3-4 hours per day": 3,
        "4-5 hours per day": 4,
        "5-6 hours per day": 5
    }

    # Return the required hours based on job type
    return options.get(job_type)


def calculate_domain_match(candidate_obj, job_obj, experience_dict, weightage, is_draft):
    """
    Calculates the domain match score for a candidate based on their experience
    and the job's domain requirements.

    Parameters:
    candidate_obj (dict): A dictionary containing information about the candidate, including their ID.
    job_obj (object): An object representing the job, which includes details about the job function.
    experience_dict (dict): A dictionary mapping candidate IDs to their experience details.
    weightage (dict): A dictionary containing the weight for domain match.
    is_draft (bool): A boolean indicating whether the job is in draft status or not.

    Returns:
    int: The domain match score based on the candidate's experience and the job's requirements.
    """
    
    # Initialize the domain match score
    domain_match = 0
    
    # Retrieve function ID and name from the job object based on whether it's a draft
    function_id = job_obj.details.get('function_id') if is_draft else job_obj.function.id
    function_name = job_obj.details.get('function_name') if is_draft else job_obj.function.tag_name
    # Check if the candidate is present in the experience dictionary
    if function_id and candidate_obj['candidate'] in experience_dict:
        for exp in experience_dict[candidate_obj['candidate']]:
            # Check if the job function is listed in the candidate's experience domains
            if function_name in exp['domains']:
                # Set domain match score based on weightage and exit the loop
                domain_match = weightage['domain']
                break
    
    return domain_match

def calculate_role_match(candidate_obj, job_obj, role_dict, weightage, is_draft):
    """
    Calculates the role match score for a candidate based on their role and the job's role requirements.

    Parameters:
    candidate_obj (dict): A dictionary containing information about the candidate, including their ID.
    job_obj (object): An object representing the job, which includes details about the job role.
    role_dict (dict): A dictionary mapping tuples of candidate IDs and role IDs to role-specific details.
    weightage (dict): A dictionary containing the weight for role match.
    is_draft (bool): A boolean indicating whether the job is in draft status or not.

    Returns:
    int: The role match score based on the candidate's role and the job's requirements.
    """
    
    # Initialize the role match score
    role_match = 0
    role = None
    # Retrieve role ID from the job object based on whether it's a draft
    if is_draft:
        role = job_obj.details.get('existing_role', {}).get('role_id')
    elif job_obj.role:
        role = job_obj.role.id
    # Check if the role is present in the role dictionary for the candidate
    if role and (candidate_obj['candidate'], role) in role_dict:
        # Set role match score based on weightage
        role_match = weightage['role']
    
    return role_match

def calculate_functional_interview_match(candidate_obj, job_skills, functional_feedback_dict, weightage):
    # fucnctional interview skills match
    functional_interview_match = 0
    skills_list = []
    # get all the ratings of candidates from the functional interviews 
    functional_feedback_skills = functional_feedback_dict.get(candidate_obj['candidate'])
    if functional_feedback_skills:
        for functional_feedback in functional_feedback_skills:
            # check if any job skills matches with candidate feedback skills 
            if functional_feedback['skill'] in job_skills:
                skills_list.append(functional_feedback['rating'])
            else:
                # if not matching the rating for that skill is zero 
                skills_list.append(0)
        # take the all the skills ratings of the candiate and take an average of it to get the score and multiply with weightage 
        functional_interview_match = (sum(skills_list)/len(skills_list)) * weightage['functional_interview']
    return functional_interview_match

def calculate_available_hours_match(candidate_obj, job_obj, weightage):
    # available hours match 
    available_hours_match = 0
    # get the minimum available hours for the job required 
    job_hours = get_job_required_hours(job_obj)
    # check if candidate has available hours 
    if job_hours and candidate_obj['total_available_hours']:
        # calculate the availability ratio by dividing through job available hours 
        availability_ratio = candidate_obj['total_available_hours'] / job_hours
        hours_weightage  = availability_ratio * weightage['total_available_hours']
        available_hours_match = min(hours_weightage, weightage['total_available_hours'])
    return available_hours_match

def calculate_relevant_exp_match(candidate_obj, job_obj, role_experience_dict, weightage, is_draft):
    """
    Calculates the relevant experience match score for a candidate based on their experience
    and the job's experience requirements.

    Parameters:
    candidate_obj (dict): A dictionary containing information about the candidate, including their ID.
    job_obj (object): An object representing the job, which includes details about the job's required experience.
    role_experience_dict (dict): A dictionary mapping tuples of candidate IDs and role IDs to lists of experience records.
    weightage (dict): A dictionary containing the weight for experience match.
    is_draft (bool): A boolean indicating whether the job is in draft status or not.

    Returns:
    int: The relevant experience match score based on the candidate's experience and the job's requirements.
    """
    
    # Initialize the relevant experience match score to 0
    experience_match = 0
    
    # Define a mapping of experience range descriptions to corresponding years
    years_options = {
        "0-3yrs": 0,
        "3-5yrs": 3,
        "5-7yrs": 5,
        "7yrs+": 7 
    }
    role_id = None
    if not is_draft:
        role_id = job_obj.role.id if job_obj.role else None
    else:
        role_id = job_obj.details.get('existing_role', {}).get('role_id')
    matched_roles = role_experience_dict.get((candidate_obj['candidate'], role_id))
    exp = job_obj.details.get('experience')
    job_experience = years_options[exp] if exp else None
    
    # If required job experience and matched roles are available
    if job_experience and matched_roles:
        year_list = []
        for matching_role in matched_roles:
            years = calculate_experience(matching_role)
            year_list.append(years)
        
        # Calculate the total experience across all matched roles
        total_exp = sum(year_list)
        
        # If the total experience meets or exceeds the required experience, assign full weightage
        if total_exp >= job_experience:
            experience_match = weightage['experience']
    
    return experience_match

def calculate_skills_match(candidate_obj, matching_data, master_skills, weightage):
    """
    Calculates the skill match score for a candidate based on their skills and the job's required skills.

    Parameters:
    candidate_obj (dict): A dictionary containing information about the candidate, including their skills.
    matching_data (dict): A dictionary containing similarity scores between candidate skills and job skills.
    master_skills (dict): A dictionary mapping candidate IDs to their master skills.
    weightage (dict): A dictionary containing the weight for skill match.

    Returns:
    int: The skill match score based on the candidate's skills and the job's requirements.
    """
    
    # Initialize the skill match score to 0
    skill_match = 0
    
    # Retrieve the master skills for the candidate (i.e., the core set of skills the candidate possesses)
    master_candidate_skills = master_skills.get(candidate_obj['candidate'], [])
    all_skills = master_candidate_skills
    
    # Add legacy skills if present (legacy skills may be older or less relevant skills that still add value)
    if candidate_obj.get('legacy_skills'):
        all_skills += candidate_obj['legacy_skills'].split(',')
    
    # Add resume skills if present (skills explicitly listed on the candidate's resume)
    if candidate_obj.get('skills_resume'):
        all_skills += candidate_obj['skills_resume']
    
    # Remove duplicate skills to ensure each skill is only considered once
    candidate_skills = {x: [] for x in all_skills}
    
    # Calculate skill similarity towards each job skill using the provided matching data
    for key in matching_data:
        # Iterate through each candidate skill
        for skill in all_skills:
            # Get the similarity score of the candidate skill towards the job skill
            # The matching_data dictionary contains pre-calculated similarity scores
            match = matching_data[key].get(skill, 0)
            # Limit the match score to a maximum of 1 to ensure that even perfect matches don't exceed this value
            match = 1 if match > 1 else match
            candidate_skills[skill].append(match)
    
    if candidate_skills:
        # For each candidate skill, find the highest similarity score with any job skill
        # This step ensures that we consider the best possible match for each skill
        total_score = sum([max(candidate_skills[x]) for x in candidate_skills]) / len(candidate_skills)
        
        # The final skill match score is calculated by multiplying the average match score 
        # by the weightage assigned to skills. This weightage determines how much importance
        # is placed on skill matching in the overall candidate-job fit.
        skill_match = total_score * weightage['skills']
    
    return skill_match

def get_work_experience_dict():
    """
    Retrieves and organizes work experience data from the database.

    Returns:
    tuple: A tuple containing three dictionaries:
        - role_experience_dict (dict): Maps tuples of candidate IDs and role IDs to lists of employment details.
        - experience_dict (dict): Maps candidate IDs to lists of employment details.
        - role_dict (dict): Maps tuples of candidate IDs and role IDs to a single employment detail entry.
    """
    
    # Fetch work experience details from the database
    work_experience = list(EmploymentDetail.objects.filter(active=True).values(
        'id', 'start_date', 'end_date', 'currently_working', 'company', 'employment_type'
    ).annotate(
        candidate=F('candidate__id'),
        role_name=F('role__tag_name'),
        domains=ArrayAgg('domains__tag_name', distinct=True),
        role=F('role__id')
    ).distinct())

    # Initialize dictionaries to store work experience data
    role_experience_dict, experience_dict, role_dict = {}, {}, {}

    for experience in work_experience:
        # Organize experience by candidate and role, with lists of experiences
        role_experience_dict.setdefault((experience['candidate'], experience['role']), []).append(experience)
        
        # Organize experience by candidate with lists of experiences
        experience_dict.setdefault(experience['candidate'], []).append(experience)
        
        # Store a single entry of experience by candidate and role
        role_dict.setdefault((experience['candidate'], experience['role']), experience)
    
    return role_experience_dict, experience_dict, role_dict

def get_flexifit_candidates(exclude_ids):
    """
    Retrieves all candidates who have cleared the Flexifit interview, excluding those with IDs in the exclude_ids list.

    Parameters:
    exclude_ids (list): A list of candidate IDs to be excluded from the results.

    Returns:
    list: A list of dictionaries containing candidate details for those who have cleared the Flexifit interview.
    """
    
    # Create a query to filter candidates who have cleared the Flexifit interview
    query = Q(status=FLEXIFIT_INTERVIEW_CLEARED)
    query &= Q(candidate__active=True)

    # Exclude candidates with IDs in the exclude_ids list if provided
    if exclude_ids:
        query &= ~Q(candidate__id__in=exclude_ids)

    # Fetch candidate details from the Flexifit model
    flexifit_objs = Flexifit.objects.filter(query).values(
        'id', 'candidate').annotate(
        legacy_skills=F('candidate__legacy_skills'),
        skills_resume=F('candidate__skills_resume'),
        total_available_hours=F('candidate__total_available_hours'),
        last_login=F('candidate__last_login'))

    # Create a dictionary to ensure unique candidates by their ID
    unique_candidates = {}
    for obj in flexifit_objs:
        unique_candidates[obj['candidate']] = obj
    
    # Return a list of unique candidates' details
    return list(unique_candidates.values())

def get_recency_match(last_login, weightage):
    """
    Determines the recency match score based on the candidate's last login date.

    Parameters:
    last_login (datetime): The last login date of the candidate.
    weightage (dict): A dictionary containing the weight for recency match.

    Returns:
    int: The recency match score based on the candidate's last login.
    """
    
    # Check if the last login date is within the defined recent period
    if last_login and last_login.date() >= datetime.datetime.now().date() - datetime.timedelta(days=EMPLOYER_LOGIN_DAYS):
        # Return the recency weight if the candidate has logged in within the recent period
        return weightage['recency']
    
    # Return 0 if the candidate's last login is outside the recent period
    return 0


def calculate_candidate_match_percentage(candidate_obj, job_obj, job_skills, matching_data, candidate_skills_dict, experience_dict, role_dict, role_experience_dict, functional_feedback_dict, weightage, is_draft):
    """
    Calculates the matching percentage between a candidate and a job based on various criteria.

    Parameters:
    candidate_obj (dict): A dictionary containing information about the candidate.
    job_obj (object): An object representing the job, including job requirements and details.
    job_skills (list): A list of required skills for the job.
    matching_data (dict): A dictionary containing similarity scores between candidate skills and job skills.
    candidate_skills_dict (dict): A dictionary mapping candidate IDs to their skills.
    experience_dict (dict): A dictionary mapping candidate IDs to lists of their work experience.
    role_dict (dict): A dictionary mapping tuples of candidate IDs and role IDs to role-specific details.
    role_experience_dict (dict): A dictionary mapping tuples of candidate IDs and role IDs to lists of experience records.
    functional_feedback_dict (dict): A dictionary containing functional interview feedback scores for candidates.
    weightage (dict): A dictionary containing weights for different match criteria.
    is_draft (bool): A boolean indicating whether the job is in draft status or not.

    Returns:
    int: The calculated matching percentage for the candidate based on the job requirements.
    """
    
    # Calculate match scores for various criteria
    domain_match = calculate_domain_match(candidate_obj, job_obj, experience_dict, weightage, is_draft)
    role_match = calculate_role_match(candidate_obj, job_obj, role_dict, weightage, is_draft)
    skill_match = calculate_skills_match(candidate_obj, matching_data, candidate_skills_dict, weightage)
    experience_match = calculate_relevant_exp_match(candidate_obj, job_obj, role_experience_dict, weightage, is_draft)
    available_hours_match = calculate_available_hours_match(candidate_obj, job_obj, weightage)
    functional_interview_match = calculate_functional_interview_match(candidate_obj, job_skills, functional_feedback_dict, weightage)
    recency_match = get_recency_match(candidate_obj['last_login'], weightage)
    
    # Compute the total weight from the weightage dictionary
    total_weight = sum(weightage.values())
    
    # Calculate the match percentage based on the sum of match scores divided by the total weight
    match_percentage = math.ceil((sum([
        domain_match, role_match, skill_match, experience_match,
        available_hours_match, functional_interview_match, recency_match
    ]) / total_weight) * 100)

    return match_percentage

def get_job_skills(job_obj, is_draft):
    """
    Retrieves all skills associated with a job, including both existing and custom skills.

    Parameters:
    job_obj (object): An object representing the job, which includes details about the job's skills.
    is_draft (bool): A boolean indicating whether the job is in draft status or not.

    Returns:
    list: A list of unique skill names associated with the job.
    """
    
    # Initialize lists for storing skills
    skills = []
    custom_skills = []
    
    # Check if the job is in draft status
    if is_draft:
        # Retrieve existing and custom skills from the job details
        skills = [x['skill_name'] for x in job_obj.details.get('existing_skills', [])]
        custom_skills = [x['skill_name'] for x in job_obj.details.get('custom_skills', [])]
    else:
        # Retrieve skills from the job's related skills and custom skills associated with the job
        skills = list(job_obj.skills.values_list('tag_name', flat=True))
        custom_skills = list(CustomSkill.objects.filter(
            jobcustomroleskills__job__id=job_obj.id, status=PENDING_STATUS).values_list('skill_name', flat=True))
    
    # Combine both lists, remove duplicates, and return the result
    return list(set(skills + custom_skills))

def get_candidate_skills():
    """
    Retrieves all active skills for candidates and organizes them by candidate ID.

    Returns:
    dict: A dictionary mapping candidate IDs to lists of their skills.
    """
    
    # Fetch all active skills from the database, including the associated candidate ID
    skills = list(Skill.objects.filter(active=True).values('tag_name').annotate(candidate=F('candidate__id')))
    
    # Initialize a dictionary to store skills for each candidate
    candidate_skills_dict = {}
    
    # Populate the dictionary with skills grouped by candidate ID
    [candidate_skills_dict.setdefault(skill['candidate'], []).append(skill['tag_name']) for skill in skills]
    
    return candidate_skills_dict

def calculate_matching_percentage(job_obj, count, job_skills, role_experience_dict, experience_dict, role_dict, candidate_id, exclude_ids=[], is_draft=False,):
    """
    Calculates the matching percentage for candidates based on job requirements and returns a list of candidates sorted by match percentage.

    Parameters:
    job_obj (object): An object representing the job, including job details and requirements.
    count (int): The number of top candidates to return based on the matching percentage.
    exclude_ids (list, optional): A list of candidate IDs to exclude from the results.
    is_draft (bool, optional): A boolean indicating whether the job is in draft status or not.

    Returns:
    tuple: A tuple containing:
        - A list of tuples with candidate IDs and their matching percentages, limited to the specified count.
        - A dictionary with candidates' work experience details.
        - A list of job skills.
    """
    
    try:
        log_data = [f"info|| {datetime.datetime.now()}: calculate matching percentage function"]
        
        # Load the weightage configuration from a JSON file
        with open('weights.json', 'r') as file:
            weightage = json.load(file)
        # get all matching skill towards each job 
        matching_data = calculate_similarity_scores(job_skills)
        
        # Retrieve candidate skills from the database
        candidate_skills_dict = get_candidate_skills()
        
        # Get functional feedback for candidates who cleared the interview
        functional_feedback = FunctionalFeedback.objects.filter(recommendation=FUNCTIONAL_INTERVIEW_CLEARED).values('skills_feedback').annotate(candidate=F('functional__candidate__id'))
        functional_feedback_dict = {}
        [functional_feedback_dict.setdefault(feedback['candidate'], []).extend(feedback['skills_feedback']) for feedback in functional_feedback]
        # get flexifit candidate details 
        flexifit_objs_list = get_flexifit_candidates(exclude_ids)       
        matching_candidates = {}
        for candidate_obj in flexifit_objs_list:
            # Calculate the match percentage for each candidate
            match_percentage = calculate_candidate_match_percentage(
                candidate_obj, job_obj, job_skills, matching_data, candidate_skills_dict,
                experience_dict, role_dict, role_experience_dict, functional_feedback_dict, weightage, is_draft
                )
            # Store candidates in the dictionary, grouped by their match percentage
            if match_percentage not in matching_candidates:
                matching_candidates[match_percentage] = []
            matching_candidates[match_percentage].append(candidate_obj['candidate'])
        
        # Sort the match percentages in descending order and prepare the final list
        sorted_keys_descending = sorted(matching_candidates.keys(), reverse=True)
        matching_candidates_list = []
        for key in sorted_keys_descending:
            matching_candidates_list.extend([(x, key) for x in matching_candidates[key]])
        return list(filter(lambda x: x[0] == candidate_id, matching_candidates_list)) if candidate_id else matching_candidates_list[:count]
    except Exception as e:
        # Log any errors encountered during the process
        log_data.append(f"error || exception :{e}")
        log_data.append("LINE_BREAK")
        api_logging(log_data)
        return Response(message_response(invalid_input), status=400)