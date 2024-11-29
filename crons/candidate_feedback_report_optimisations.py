import logging
import base64
import os
import time
from sendgrid.helpers.mail import Mail, Attachment
from flexibees_finance.settings import SENDGRID_API_KEY, FROM_EMAIL
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from apps.candidate.models import ClientFeedback, Functional, \
     AssignmentFeedback, FunctionalFeedback, FlexifitFeedback
from sendgrid import SendGridAPIClient, FileContent, FileType, FileName, Disposition
import pandas as pd
import numpy as np


id_lists = []

# defining a function for getting skill wise score for candidates
def skills_score(func_fb_obj):
    skills = ""
    count = len(func_fb_obj.skills_feedback)
    for skill in func_fb_obj.skills_feedback:
        skills += f"{skill['skill']} - {skill['rating']}"
        count -= 1
        if count > 0:
            skills += "\n"
    return f"{skills}"

# defining a function for getting skill_score and over_all score
def add_skill_score(can_id,proj_id,client_data):
    functional_id = Functional.objects.get(candidate_id=can_id, project_id=proj_id).pk
    func_fb_obj = FunctionalFeedback.objects.filter(functional_id=functional_id).first()
    if func_fb_obj:
        functional_fb_comments = func_fb_obj.comments
        client_data['FunctionalFeedback'] = functional_fb_comments
        client_data["Skills_Score"] = skills_score(func_fb_obj)
        client_data["Overall_Score"] = func_fb_obj.overall_score

# grouping all the common data present in each feedback function
def extract_common_data(obj, client_data):
    client_data['Client Name'] = obj.project.deal_name
    client_data['Role'] = obj.project.role
    client_data['BD Manager'] = obj.project.bd
    client_data['Recruiter'] = obj.project.recruiter
    client_data['Candidate name'] = obj.candidate.first_name

# defining a function to give the flexibit feedback comments
def add_flexifit_feedback_comments(candidate_id,proj_id,client_data):
    flexifit_fb = list(FlexifitFeedback.objects.filter(flexifit__candidate_id=candidate_id,
                                        flexifit__project_id=proj_id).values_list('comments',flat=True))
    if flexifit_fb:
        client_data['FlexifitFeedback'] = ' || '.join(flexifit_fb)



# defining a function to give the functional feedback comments for re-usability
def add_functional_feedback_comments(candidate_id,proj_id,client_data):
    functional_fb = list(FunctionalFeedback.objects.filter(functional__candidate_id=candidate_id,
                                        functional__project_id=proj_id).values_list('comments',flat=True))
    if functional_fb:
        client_data['FunctionalFeedback'] = ' || '.join(functional_fb)

# defining a function to give the assignment feedback comments for re-usability
def add_assignment_feedback_comments(candidate_id,proj_id,client_data):
    assignment_fb = list(AssignmentFeedback.objects.filter(assignment__candidate_id=candidate_id,
                                        assignment__project_id=proj_id).values_list('comments',flat=True))
    if assignment_fb:
        client_data['AssignmentFeedback'] = ' || '.join(assignment_fb)

# for getting the client feedback data
def extract_client_feedback_data(client_data, data, feedback_list,id_lists):
    extract_common_data(data.final_selection, client_data)
    client_data['ClientFeedback'] = data.comments
    client_data['Selected'] = data.get_recommendation_display()
    can_id = data.final_selection.candidate.id
    proj_id = data.final_selection.project_id
    id_lists.append((can_id,proj_id))
    add_skill_score(can_id,proj_id,client_data)
    try:
        add_flexifit_feedback_comments(can_id,proj_id,client_data)
        add_assignment_feedback_comments(can_id,proj_id,client_data)
    except Exception as e:
        logging.error(f'Error: {str(e)}')
    feedback_list.append(client_data)

# for getting the flexifit feedback data
def extract_flexifit_feedback_data(client_data, data, feedback_list,id_lists):
    can_id = data.flexifit.candidate.id
    proj_id = data.flexifit.project_id
    # ensure that there is no duplicate data
    if (can_id,proj_id) not in id_lists:
        extract_common_data(data.flexifit, client_data)
        client_data['FlexifitFeedback'] = data.comments
        id_lists.append((can_id, proj_id))
        add_skill_score(can_id,proj_id,client_data)
        try:
            add_assignment_feedback_comments(can_id,proj_id,client_data)
        except Exception as e:
            logging.error(f'Error: {str(e)}')
        feedback_list.append(client_data)

# for getting the functional feedback data
def extract_functional_feedback_data(client_data, data, feedback_list,id_lists):
    can_id = data.functional.candidate.id
    proj_id = data.functional.project.id
    # ensure that there is no duplicate data
    if (can_id,proj_id) not in id_lists:
        extract_common_data(data.functional, client_data)
        client_data['FunctionalFeedback'] = data.comments
        id_lists.append((can_id, proj_id))
        functional_id = Functional.objects.get(candidate_id=data.flexifit.candidate.id,project_id=data.flexifit.project_id).pk
        func_fb_obj = FunctionalFeedback.objects.filter(functional_id=functional_id).first()
        client_data["Skills_Score"] = skills_score(func_fb_obj)
        client_data['Overall_Score'] = data.overall_score
        try:
            add_assignment_feedback_comments(can_id,proj_id,client_data)
        except Exception as e:
            logging.error(f'Error: {str(e)}')
        feedback_list.append(client_data)

# for getting the assignment feedback data
def extract_assignment_feedback_data(client_data, data, feedback_list,id_lists):
    # ensure that there is no duplicate data
    if (data.assignment.candidate.id,data.assignment.project_id) not in id_lists:
        extract_common_data(data.assignment, client_data)
        client_data['AssignmentFeedback'] = data.comments
        feedback_list.append(client_data)


def candidate_feedback_report(queryset, feedback_list):
    # setting the number of records to be processed at once
    page_size = 2000
    page_no = 1
    # slicing the number of records to be processed at once
    pages = Paginator(queryset, page_size)
    while page_no <= pages.num_pages:
        # assigning the records to be processed at once
        queryset = pages.get_page(page_no)
        for data in queryset:
            client_data = {'Client Name': '', 'Role': '', 'BD Manager': '', 'Recruiter': '', 'Candidate name': '',
                           'AssignmentFeedback': '', 'FunctionalFeedback': '', 'Skills_Score':'', 'Overall_Score':'',
                           'FlexifitFeedback': '', 'ClientFeedback': '', 'Selected': ''}
            try:
                # check  the data is having client feedback
                if isinstance(data, ClientFeedback):
                    extract_client_feedback_data(client_data, data, feedback_list,id_lists)
                # check  the data is having flexifit feedback
                elif isinstance(data, FlexifitFeedback):
                    extract_flexifit_feedback_data(client_data, data, feedback_list,id_lists)
                # check  the data is having functional feedback
                elif isinstance(data, FunctionalFeedback):
                    extract_functional_feedback_data(client_data, data, feedback_list,id_lists)
                # check  the data is having assignment feedback
                elif isinstance(data, AssignmentFeedback):
                    extract_assignment_feedback_data(client_data, data, feedback_list,id_lists)
            except Exception as e:
                feedback_list.append(client_data)
                logging.error(f'Error occured at {page_no}')
        # increasing the page number to process the remaining records
        page_no += 1
        # setting the process to sleep for 2 seconds so that it takes time and the remaining process also will keep running
        time.sleep(2)


def main():
    feedback_list = []
    # getting all the data present in their respective feedback data
    client_feedback = ClientFeedback.objects.all().order_by('id')
    flexifit_feedback = FlexifitFeedback.objects.all().order_by('id')
    functional_feedback = FunctionalFeedback.objects.all().order_by('id')
    assignment_feedback = AssignmentFeedback.objects.all().order_by('id')

    #calling the functions with respective to their feedback
    candidate_feedback_report(client_feedback, feedback_list)
    candidate_feedback_report(flexifit_feedback, feedback_list)
    candidate_feedback_report(functional_feedback, feedback_list)
    candidate_feedback_report(assignment_feedback, feedback_list)

    if len(feedback_list) == 0:
        try:
            template = 'empty_candidate_feedback_report.html'
            msg_html = render_to_string(template)
            message = Mail(
                from_email=FROM_EMAIL,
                to_emails=['rashmi@flexibees.com'],
                # to_emails=['girish@appinessworld.com','gurusharan@appinessworld.com','kiran@appinessworld.com'],
                subject='Candidate Feedback Report',
                html_content=msg_html
            )
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
        except Exception as e:
            logging.error(f'unable to send mail: Error{str(e)}')
        finally:
            return
    try:
        df = pd.DataFrame(data=feedback_list)
        df = df.sort_values(by=['Client Name'])
        df.index = np.arange(1, len(df) + 1)
        candidate_file = 'Candidate Feedback Report.xlsx'
        df.to_excel(candidate_file)
        template = 'candidate_feedback_report.html'
        msg_html = render_to_string(template)
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=['rashmi@flexibees.com'],
            # to_emails=['girish@appinessworld.com', 'gurusharan@appinessworld.com', 'kiran@appinessworld.com'],
            subject='Candidate Feedback Report',
            html_content=msg_html
        )
        with open(candidate_file, 'rb') as f:
            candidates_data = f.read()
            f.close()
        encoded_file = base64.b64encode(candidates_data).decode()
        attached_file = Attachment(
            FileContent(encoded_file),
            FileName(candidate_file),
            FileType('application/ms-excel'),
            Disposition('attachment')
        )
        message.attachment = attached_file
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        os.unlink(candidate_file)
    except Exception as e:
        logging.error(f'unable to send mail: Error{str(e)}')

    return True
