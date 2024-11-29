import logging
import base64
import os
from sendgrid.helpers.mail import Mail, Attachment
from flexibees_finance.settings import file_path, SENDGRID_API_KEY, FROM_EMAIL
from django.template.loader import render_to_string
from apps.candidate.models import Candidate, ClientFeedback, FinalSelection, \
    Assignment, AssignmentFeedback, Functional, FunctionalFeedback, FlexifitFeedback, Flexifit
from django.utils.timezone import now, timedelta
from sendgrid import SendGridAPIClient, FileContent, FileType, FileName, Disposition
import pandas as pd
import numpy as np
from itertools import chain
from flexibees_finance.settings import TO_EMAIL, RECEIVER_NAME


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


def candidate_feedback_report(all_candidates=False):
    date = now() - timedelta(days=7)
    start_date = date.strftime('%d%b%Y')
    end_date = now().strftime('%d%b%Y')
    feedback_list=[]
    id_lists=[]
    if all_candidates:
        clientfeedback_query=ClientFeedback.objects.exclude(final_selection__isnull=True)
        flexifitfeedback_query = FlexifitFeedback.objects.all()
        functional_query=FunctionalFeedback.objects.all()
        assign_query = AssignmentFeedback.objects.all()
    else:
        clientfeedback_query=ClientFeedback.objects.filter(created__gt=date).exclude(final_selection__isnull=True)
        flexifitfeedback_query = FlexifitFeedback.objects.filter(created__gt=date)
        functional_query=FunctionalFeedback.objects.filter(created__gt=date)
        assign_query = AssignmentFeedback.objects.filter(created__gt=date)
    feedback_query=list(chain(clientfeedback_query,flexifitfeedback_query,functional_query,assign_query))
    if feedback_query is not None:
        for data in feedback_query:
            project_details = []
            try:
                client_data = {'Project Id': '', 'Client Name': '', 'Role': '', 'BD Manager': '', 'Recruiter': '', 'Candidate Id': '', 'Candidate name': '',
                               'AssignmentFeedback': '', 'FunctionalFeedback': '', 'Skills_Score':'', 'Overall_Score':'',
                               'FlexifitFeedback': '', 'ClientFeedback': '', 'Selected': ''}
                feedback_from=data.__class__.__name__
                if feedback_from =='ClientFeedback':
                    # check  the data is having client feedback
                    project_details.append(data.final_selection.candidate.id)
                    project_details.append(data.final_selection.project.id)
                    id_lists.append(project_details)
                    client_data['Client Name'] = data.final_selection.project.company_name
                    client_data['Role'] = data.final_selection.project.role
                    client_data['BD Manager'] = data.final_selection.project.bd
                    client_data['Recruiter'] = data.final_selection.project.recruiter
                    client_data['Candidate name'] = data.final_selection.candidate.first_name
                    client_data['Candidate Id'] = data.final_selection.candidate.id
                    client_data['Project Id'] = data.final_selection.project.id
                    client_data['ClientFeedback'] = data.comments
                    client_data['Selected'] = data.get_recommendation_display()
                    flexifit_id = Flexifit.objects.get(candidate_id=data.final_selection.candidate.id,
                                                       project_id=data.final_selection.project_id).pk
                    flexifit_fb_comments = FlexifitFeedback.objects.get(flexifit_id=flexifit_id).comments
                    client_data['FlexifitFeedback'] = flexifit_fb_comments
                    functional_id = Functional.objects.get(candidate_id=data.final_selection.candidate.id,
                                                        project_id=data.final_selection.project_id).pk
                    func_fb_obj = FunctionalFeedback.objects.filter(functional_id=functional_id).first()
                    if func_fb_obj:
                        functional_fb_comments = func_fb_obj.comments
                        client_data['FunctionalFeedback'] = functional_fb_comments
                        client_data["Skills_Score"] = skills_score(func_fb_obj)
                        client_data["Overall_Score"] = func_fb_obj.overall_score
                    assignment = Assignment.objects.get(candidate_id=data.final_selection.candidate.id,
                                                        project_id=data.final_selection.project_id).pk
                    assignment_fb_comments = AssignmentFeedback.objects.get(assignment_id=assignment).comments
                    client_data['AssignmentFeedback'] = assignment_fb_comments
                    feedback_list.append(client_data)
                elif feedback_from =='FlexifitFeedback':
                    count = 0
                    for i in id_lists:
                        if data.flexifit.candidate.id == i[0] and data.flexifit.project.id == i[1]:
                            count += 1
                    # ensure that there is duplicate data
                    if count == 0:
                        project_details.append(data.flexifit.candidate.id)
                        project_details.append(data.flexifit.project.id)
                        id_lists.append(project_details)
                        client_data['Client Name'] = data.flexifit.project.company_name
                        client_data['Role'] = data.flexifit.project.role
                        client_data['BD Manager'] = data.flexifit.project.bd
                        client_data['Recruiter'] = data.flexifit.project.recruiter
                        client_data['Candidate name'] = data.flexifit.candidate.first_name
                        client_data['Candidate Id'] = data.flexifit.candidate.id
                        client_data['Project Id'] = data.flexifit.project.id
                        client_data['FlexifitFeedback'] = data.comments
                        functional_id = Functional.objects.get(candidate_id=data.flexifit.candidate.id,
                                                               project_id=data.flexifit.project_id).pk
                        func_fb_obj = FunctionalFeedback.objects.filter(functional_id=functional_id).first()
                        if func_fb_obj:
                            functional_fb_comments = func_fb_obj.comments
                            client_data['FunctionalFeedback'] = functional_fb_comments
                            client_data["Skills_Score"] = skills_score(func_fb_obj)
                            client_data["Overall_Score"] = func_fb_obj.overall_score
                        assignment_id = Assignment.objects.get(candidate_id=data.flexifit.candidate.id,
                                                               project_id=data.flexifit.project_id).pk
                        assignment_fb_comments = AssignmentFeedback.objects.get(assignment_id=assignment_id).comments
                        client_data['AssignmentFeedback'] = assignment_fb_comments
                        feedback_list.append(client_data)
                elif feedback_from =='FunctionalFeedback':
                    count = 0
                    for i in id_lists:
                        if data.functional.candidate.id == i[0] and data.functional.project.id == i[1]:
                            count += 1
                    # ensure that there is duplicate data
                    if count == 0:
                        project_details.append(data.functional.candidate.id)
                        project_details.append(data.functional.project.id)
                        id_lists.append(project_details)
                        client_data['Client Name'] = data.functional.project.company_name
                        client_data['Role'] = data.functional.project.role
                        client_data['BD Manager'] = data.functional.project.bd
                        client_data['Recruiter'] = data.functional.project.recruiter
                        client_data['Candidate name'] = data.functional.candidate.first_name
                        client_data['Candidate Id'] = data.functional.candidate.id
                        client_data['Project Id'] = data.functional.project.id
                        client_data['FunctionalFeedback'] = data.comments
                        client_data["Skills_Score"] = skills_score(func_fb_obj)
                        client_data['Overall_Score'] = data.overall_score
                        assignment_id = Assignment.objects.get(candidate_id=data.functional.candidate.id,
                                                               project_id=data.functional.project.id).pk
                        assignment_fb_comments = AssignmentFeedback.objects.get(assignment_id=assignment_id).comments
                        client_data['AssignmentFeedback'] = assignment_fb_comments
                        feedback_list.append(client_data)
                        project_details.append(data.functional.candidate.id)
                        project_details.append(data.functional.project.id)
                        id_lists.append(project_details)
                else:
                    count = 0
                    for i in id_lists:
                        if data.assignment.candidate.id == i[0] and data.assignment.project.id == i[1]:
                            count += 1
                    # ensure that there is no duplicate data
                    if count == 0:
                        client_data['Client Name'] = data.assignment.project.company_name
                        client_data['Role'] = data.assignment.project.role
                        client_data['BD Manager'] = data.assignment.project.bd
                        client_data['Recruiter'] = data.assignment.project.recruiter
                        client_data['Candidate name'] = data.assignment.candidate.first_name
                        client_data['Candidate Id'] = data.assignment.candidate.id
                        client_data['Project Id'] = data.assignment.project.id
                        client_data['AssignmentFeedback'] = data.comments
                        feedback_list.append(client_data)
            except Exception as e:
                  feedback_list.append(client_data)
                  logging.error(f'Error{str(e)}')
                  continue
        try:
            df = pd.DataFrame(data=feedback_list)
            df = df.sort_values(by=['Client Name'])
            df.index = np.arange(1, len(df) + 1)
            candidate_file = 'All candidates feedback report.xlsx' if all_candidates else 'Candidate Feedback Report from '+ start_date+ ' to ' + end_date + '.xlsx'
            df.to_excel(candidate_file)
            template = 'candidate_feedback_report.html'
            if all_candidates:
                context = {'title':'All candidates feedback report', 'body_title':f"All candidates feedback report", 'reciever_name': RECEIVER_NAME}
            else:
                context = {'title': f"Candidate feedback report from { start_date } to { end_date }", 'body_title':f"Candidates weekly feedback Report for the period of { start_date } to { end_date } .", 'reciever_name': RECEIVER_NAME}
            msg_html = render_to_string(template, context)
            message = Mail(
                from_email=FROM_EMAIL,
                to_emails=[TO_EMAIL,],
                subject=context['title'],
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

    else:
        try:
            template = 'empty_candidate_feedback_report.html'
            if all_candidates:
                context = {'title':f"All candidates feedback report", 'body_title':f"There is no candidate feedback .", 'reciever_name':RECEIVER_NAME}
            else:
                context = {'title': f"Candidate feedback report from { start_date } to { end_date }", 'body_title':f"From { start_date } to { end_date } there is no candidate feedback .", 'reciever_name':RECEIVER_NAME}
            msg_html = render_to_string(template, context)
            message = Mail(
                from_email=FROM_EMAIL,
                to_emails=[TO_EMAIL,],
                subject=context['title'],
                html_content=msg_html
            )
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            sg.send(message)
        except Exception as e:
               logging.error(f'unable to send mail: Error{str(e)}')
    return True
