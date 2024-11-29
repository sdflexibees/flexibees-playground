import logging
import base64
import os

import pytz
from sendgrid.helpers.mail import Mail, Attachment

from apps.admin_app.models import Skill
from flexibees_finance.settings import file_path, SENDGRID_API_KEY, FROM_EMAIL
from django.template.loader import render_to_string
from apps.candidate.models import Candidate, ClientFeedback, FinalSelection, Flexifit
from apps.projects.models import Project, Pricing
from django.utils.timezone import now, timedelta
from sendgrid import SendGridAPIClient, FileContent, FileType, FileName, Disposition
import pandas as pd
import numpy as np


def get_date_time(dt, return_date=False):
    date_fmt = "%d-%m-%Y"
    dt_fmt = "%d-%m-%Y  %H:%M:%S"
    return dt.astimezone(pytz.timezone('Asia/Kolkata')).strftime(date_fmt if return_date else dt_fmt)


# check while calling this function this is same as recruitment dashboard report but few columns are 
# not added in this report and also the new columns are added in the candidate model
def recruitment_progress_dashboard():
    date = now() - timedelta(days=7)
    start_date = date.strftime('%d%b%Y')
    end_date = now().strftime('%d%b%Y')
    recruiter_data=[]
    project_query=Project.objects.prefetch_related('finalselection_set','pricing_set').filter(modified__gt=date)
    if project_query is not None:
       for project in project_query:
           try:
                 each_record = {'Client Name': '', 'Role': '', 'BD Manager': '', 'Recruiter': '', 'CRM date': '',
                               'Date sent requesting candidate Salary': '',
                               'Date received candidate salary': '', 'Date sent to recruitment': '',
                               'Assigned to recruiter': '',
                               'First time a candidate moves to every new stage': '',
                               'First final candidate profile sent to BD manager': '',
                               'Date of client feedback/ Candidate selected': '', 'Date of Candidate selected': '',
                               'Resumes sent': '',
                               'Number of profiles sent': '', 'selected': '', 'Number of selected candidate': '',
                               'Final confirmed salary range': '',
                               'Type of Payout':''}
                 final_candidate=project.finalselection_set.filter(project_id=project.id)
                 if len(final_candidate)>0:
                     for final in final_candidate:
                         try:
                             each_record['First time a candidate moves to every new stage'] = get_date_time(final.created, return_date=True)
                             each_record['Client Name'] = project.deal_name
                             each_record['Role'] = project.role
                             each_record['BD Manager'] = project.bd
                             each_record['Recruiter'] = project.recruiter
                             each_record['CRM date'] = get_date_time(project.created,return_date=True)

                             # After update project details project sent to recruiter admin
                             each_record['Date sent to recruitment'] = get_date_time(project.request_date, return_date=True)

                             # Pricing details
                             pricing_sent = project.pricing_set.get(project_id=project.id,stage=1)
                             each_record['Date sent requesting candidate Salary'] = get_date_time(pricing_sent.created)

                             pricing_recieve = project.pricing_set.get(project_id=project.id,stage=4)
                             each_record['Date received candidate salary'] = get_date_time(pricing_recieve.created)
                             min_salary = pricing_recieve.min_salary
                             max_salary = pricing_recieve.max_salary
                             each_record['Final confirmed salary range'] = f"{min_salary} - {max_salary}"
                             each_record['Type of Payout'] = pricing_sent.type_of_payout

                             # Count of candidates related to corresponding  project
                             if project.flexibees_selected > 0:
                                 each_record['Resumes sent'] = 'Yes'
                                 each_record['Number of profiles sent'] = project.flexibees_selected
                             else:
                                 each_record['Resumes sent'] = 'No'
                                 each_record['Number of profiles sent'] = 0
                             if project.client_selected > 0:
                                 each_record['selected'] = 'Yes'
                                 each_record['Number of selected candidate'] = project.flexibees_selected
                             else:
                                 each_record['selected'] = 'No'
                                 each_record['Number of selected candidate'] = 0
                             each_record['First final candidate profile sent to BD manager'] = get_date_time(project.send_to_bdmanager, return_date=True)
                             client_fb = ClientFeedback.objects.get(final_selection_id=final.id)
                             each_record['Date of client feedback/ Candidate selected'] = get_date_time(client_fb.created, return_date=True)
                             each_record['Date of Candidate selected'] = get_date_time(client_fb.created, return_date=True)
                             # after getting proposed salary from client project assigned to recruiter
                             each_record['Assigned to recruiter'] = get_date_time(project.date_assigned_to_recruiter,return_date=True)
                             recruiter_data.append(each_record)
                         except:
                             recruiter_data.append(each_record)
                             continue
                 else:
                     each_record['Client Name'] = project.deal_name
                     each_record['Role'] = project.role
                     each_record['BD Manager'] = project.bd
                     each_record['Recruiter'] = project.recruiter
                     each_record['CRM date'] = get_date_time(project.created,return_date=True)

                     # After update project details project sent to recruiter admin
                     each_record['Date sent to recruitment'] = get_date_time(project.request_date,return_date=True)

                     # Pricing details
                     pricing_sent = Pricing.objects.get(project_id=project.id, stage=1)
                     each_record['Date sent requesting candidate Salary'] = get_date_time(pricing_sent.created)

                     pricing_recieve = Pricing.objects.get(project_id=project.id, stage=4)
                     each_record['Date received candidate salary'] = get_date_time(pricing_recieve.created)
                     min_salary = pricing_recieve.min_salary
                     max_salary = pricing_recieve.max_salary
                     each_record['Final confirmed salary range'] = f"{min_salary} - {max_salary}"
                     each_record['Type of Payout'] = pricing_sent.type_of_payout

                     if project.flexibees_selected > 0:
                         each_record['Resumes sent'] = 'Yes'
                         each_record['Number of profiles sent'] = project.flexibees_selected
                     else:
                         each_record['Resumes sent'] = 'No'
                         each_record['Number of profiles sent'] = 0
                     if project.client_selected > 0:
                         each_record['selected'] = 'Yes'
                         each_record['Number of selected candidate'] = project.flexibees_selected
                     else:
                         each_record['selected'] = 'No'
                         each_record['Number of selected candidate'] = 0
                     # after getting proposed salary from client project assigned to recruiter
                     each_record['Assigned to recruiter'] = get_date_time(project.date_assigned_to_recruiter,return_date=True)
                     recruiter_data.append(each_record)
           except Exception as e:
               recruiter_data.append(each_record)
               continue;
       try:
            if recruiter_data is not None:
                # write the data into excel sheet using dataframe
                df = pd.DataFrame(data=recruiter_data)
                df.index = np.arange(1, len(df) + 1)
                recruiter_file = 'Recruiter_Progress_dashboard from '+ start_date+' to '+ end_date + '.xlsx'
                df.to_excel(recruiter_file)
                template = 'recruitement_dashboard.html'
                context = {'start_date': start_date, 'end_date': end_date}
                msg_html = render_to_string(template, context)
                message = Mail(
                    from_email=FROM_EMAIL,
                    to_emails=['rashmi@flexibees.com'],
                    # to_emails=['kiran@appinessworld.com'],
                    subject='Recruiter_Progress_dashboard from ' + start_date + ' to ' + end_date,
                    html_content=msg_html
                )
                with open(recruiter_file, 'rb') as f:
                    candidates_data = f.read()
                    f.close()
                encoded_file = base64.b64encode(candidates_data).decode()
                attached_file = Attachment(
                    FileContent(encoded_file),
                    FileName(recruiter_file),
                    FileType('application/ms-excel'),
                    Disposition('attachment')
                )
                message.attachment = attached_file
                sg = SendGridAPIClient(SENDGRID_API_KEY)
                sg.send(message)
                os.unlink(recruiter_file)
       except Exception as e:
               logging.error(f'unable to send mail: Error{str(e)}')

    else:
        template = 'empty_recruiter_progress_dashboard.html'
        context = {'start_date': start_date, 'end_date': end_date, 'reciever_name': 'Rashmi'}
        msg_html = render_to_string(template, context)
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=['rashmi@flexibees.com'],
            # to_emails=['kiran@appinessworld.com'],
            subject='Recruiter_Progress_dashboard from ' + start_date + ' to ' + end_date,
            html_content=msg_html
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)