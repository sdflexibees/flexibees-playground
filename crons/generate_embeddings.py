import datetime
import json
import os
from apps.admin_app.models import Skill
from apps.admin_app.views import api_logging
from apps.candidate.models import FunctionalFeedback
from django.db.models import F
from apps.employer.constants import FUNCTIONAL_INTERVIEW_CLEARED
import torch
from core.matching import st_model, device

def generate():
    """
    Save embeddings and skills in a file.
    
    This function performs the following tasks:
    1. Aggregates all unique skills related to candidates who have cleared the functional interview.
    2. Generates embeddings for these skills using a pre-trained model.
    3. Saves the embeddings to a file named 'candidate_embeddings.pt'.
    4. Saves the list of unique candidate skills to a JSON file named 'candidate_skills.json'.
    """

    log_data = [f"info|| {datetime.datetime.now()}: Exception occurred generating the embeddings"]
    try:
        # Define file names for storing embeddings and skills
        candidate_embeddings_file = 'candidate_embeddings.pt'
        candidate_skills_file = 'candidate_skills.json'

        # Retrieve relevant candidate data from the database
        functional = 'functional__candidate__'
        candidates = FunctionalFeedback.objects.filter(recommendation=FUNCTIONAL_INTERVIEW_CLEARED, active=True).values('id').annotate(
            legacy_skills=F(f'{functional}legacy_skills'), 
            skills_resume=F(f'{functional}skills_resume'), 
            candidate_id=F(f'{functional}id'))

        # Gather all skills associated with the candidates
        skills = list(Skill.objects.filter(candidate__id__in =[x['candidate_id'] for x in candidates], active=True).values_list('tag_name', flat=True))
        candidate_skills = []
        for candidate in candidates:
            if candidate['legacy_skills']:
                candidate_skills.extend([x.strip() for x in candidate['legacy_skills'].split(',')])
            if candidate['skills_resume']:
                candidate_skills.extend([x.strip() for x in candidate['skills_resume']])
        
        # Create a unique list of candidate skills
        candidate_skills = list(set(list(candidate_skills + skills)))

        # Generate embeddings for the candidate skills
        candidate_embeddings = st_model.encode(candidate_skills, convert_to_tensor=True).to(device)

        # Remove the existing files if they exist
        if os.path.exists(candidate_embeddings_file):
            os.remove(candidate_embeddings_file)
        if os.path.exists(candidate_skills_file):
            os.remove(candidate_skills_file)

        # Save the generated embeddings to a file
        torch.save(candidate_embeddings.cpu(), candidate_embeddings_file)

        # Save the candidate skills to a JSON file
        with open(candidate_skills_file, 'w') as json_file:
            json.dump(candidate_skills, json_file, indent=4)

        return True
    except Exception as e:
        log_data.append(f"error|| {e}")
        api_logging(log_data)
        return False
