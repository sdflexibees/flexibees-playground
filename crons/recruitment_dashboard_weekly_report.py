import logging
import base64
import os

import pytz
from sendgrid.helpers.mail import Mail, Attachment

from apps.admin_app.models import Skill
from flexibees_candidate.settings import file_path, SENDGRID_API_KEY, FROM_EMAIL
from django.template.loader import render_to_string
from apps.candidate.models import Candidate, ClientFeedback, FinalSelection, Flexifit
from apps.projects.models import Project, Pricing
from django.utils.timezone import now, timedelta
from sendgrid import SendGridAPIClient, FileContent, FileType, FileName, Disposition
import pandas as pd
import numpy as np
from flexibees_candidate.settings import TO_EMAIL


def get_date_time(dt, return_date=False):
    date_fmt = "%d-%m-%Y"
    dt_fmt = "%d-%m-%Y  %H:%M:%S"
    return dt.astimezone(pytz.timezone('Asia/Kolkata')).strftime(date_fmt if return_date else dt_fmt)


def recruitment_progress_dashboard(all_candidates=False):
    date = now() - timedelta(days=7)
    start_date = date.strftime('%d%b%Y')
    end_date = now().strftime('%d%b%Y')
    recruiter_data = []
    client_selected_count = {}
    ids_list = set()
    data = {'Project Id':'', 'Client Name': '', 'Role': '', 'BD Manager': '', 'Recruiter': '', 'CRM date': '',
            'Date sent to profile table': '','Date received first candidate salary': '', 
            'Date proposed client pricing': '', 'Date sent final client pricing': '',
            'Date moved to recruitment after final salary': '', 'Date assigned to recruiter': '',
            'First time a candidate moves to every new stage': '',
            'First final candidate profile sent to BD manager': '',
            'Date of client feedback': '', 'Date of Candidate selected': '',
            'Resumes sent': '',
            'Number of profiles sent': '', 'selected': '', 'Number of selected candidate': '',
            'Candidate Proposed salary range': '',
            'Final confirmed salary range': '',
            'Type of Payout':'',
            'Total No. of Recruitment Days for First Final Selection ': '',
            'Total No. of Recruitment days for Client Selected Candidate ': ''}
    if all_candidates:
        project_query = Project.objects.prefetch_related('finalselection_set', 'pricing_set').distinct()
    else:
        project_query = Project.objects.prefetch_related('finalselection_set', 'pricing_set').filter(modified__gt=date).distinct()
    if project_query is not None:
        for project in project_query:
            try:
                each_record = data.copy()
                final_candidate = project.finalselection_set.filter(project_id=project.id).order_by('id')
                if len(final_candidate) > 0:
                    if project.id in ids_list:
                        continue
                    ids_list.add(project.id)
                    try:
                        each_record['First time a candidate moves to every new stage'] = get_date_time(final_candidate[0].created, return_date=True)
                        each_record['Client Name'] = project.company_name
                        each_record['Project Id'] = project.id
                        each_record['Role'] = project.role
                        each_record['BD Manager'] = project.bd
                        each_record['Recruiter'] = project.recruiter
                        each_record['CRM date'] = get_date_time(project.created, return_date=True)
                        # After update project details project sent to recruiter admin
                        each_record['Date sent to profile table'] = get_date_time(project.request_date, return_date=True)
                        # Pricing details
                        pricing_sent = project.pricing_set.filter(project_id=project.id).order_by('created')
                        pricing_length = len(list(pricing_sent))
                        if pricing_length > 0:
                            min_salary = pricing_sent[0].min_salary
                            max_salary = pricing_sent[0].max_salary
                            each_record['Candidate Proposed salary range'] = f"{min_salary} - {max_salary}"
                            each_record['Date received first candidate salary'] = get_date_time(pricing_sent[0].created)
                            each_record['Type of Payout'] = pricing_sent[0].type_of_payout
                            if pricing_length > 1:
                                each_record['Date proposed client pricing'] = get_date_time(pricing_sent[1].created)
                            if pricing_length > 2:
                                each_record['Date sent final client pricing'] = get_date_time(pricing_sent[2].created)
                            if pricing_length > 3:
                                min_salary = pricing_sent[3].min_salary
                                max_salary = pricing_sent[3].max_salary
                                each_record['Final confirmed salary range'] = f"{min_salary} - {max_salary}"
                            # Count of candidates related to corresponding  project
                            if pricing_length == 4:
                                if project.flexibees_selected > 0:
                                    each_record['Resumes sent'] = 'Yes'
                                    each_record['Number of profiles sent'] = project.flexibees_selected
                                else:
                                    each_record['Resumes sent'] = 'No'
                                    each_record['Number of profiles sent'] = 0
                                if project.id in client_selected_count:
                                    if client_selected_count[str(project.id)] > 0:
                                        each_record['selected'] = 'Yes'
                                        each_record['Number of selected candidate'] = client_selected_count[str(project.id)]
                                    else:
                                        each_record['selected'] = 'No'
                                        each_record['Number of selected candidate'] = 0
                                else:
                                    selected_count = project.finalselection_set.filter(active=True, status__in=[3,5,6]).count()
                                    client_selected_count[str(project.id)] = selected_count
                                    if selected_count > 0:
                                        each_record['selected'] = 'Yes'
                                        each_record['Number of selected candidate'] = selected_count
                                    else:
                                        each_record['selected'] = 'No'
                                        each_record['Number of selected candidate'] = 0
                                if project.date_assigned_to_recruiter:
                                    each_record['Date assigned to recruiter'] = get_date_time(project.date_assigned_to_recruiter, return_date=True)
                                # after getting proposed salary the project is moved to recruitment
                                each_record['Date moved to recruitment after final salary'] = get_date_time(project.date_sent_to_recruitment, return_date=True)
                                each_record['First final candidate profile sent to BD manager'] = get_date_time(project.send_to_bdmanager, return_date=True)
                                date1 = project.date_assigned_to_recruiter.date() if project.date_assigned_to_recruiter else project.date_sent_to_recruitment.date()
                                date2 = project.send_to_bdmanager.date()
                                delta = date2 - date1
                                if date1.weekday() in [5, 6] and date2.weekday() in [5, 6]:
                                    if date1 == date2:
                                        each_record['Total No. of Recruitment Days for First Final Selection '] = 1
                                    else:
                                        each_record['Total No. of Recruitment Days for First Final Selection '] = delta.days + 1
                                elif date1.weekday() in [5, 6] or date2.weekday() in [5, 6]:
                                    each_record['Total No. of Recruitment Days for First Final Selection '] = delta.days + 1
                                else:
                                    each_record['Total No. of Recruitment Days for First Final Selection '] = np.busday_count(date1,date2) + 1
                                client_fb = ClientFeedback.objects.filter(final_selection__project_id=project.id).order_by('id').first()
                                if client_fb is not None:
                                    each_record['Date of client feedback'] = get_date_time(client_fb.created, return_date=True)
                                first_client_selected = ClientFeedback.objects.filter(final_selection__project_id=project.id, recommendation__in=[3, 5]).order_by('id').first()
                                if first_client_selected is not None:
                                    each_record['Date of Candidate selected'] = get_date_time(client_fb.created,return_date=True)
                                if first_client_selected is not None:
                                    send_to_bdmanager = first_client_selected.created
                                    if send_to_bdmanager is not None:
                                        date = send_to_bdmanager.date()
                                        delta = date - date1
                                        if date1.weekday() in [5, 6] and date.weekday() in [5, 6]:
                                            if date1 == date:
                                                each_record['Total No. of Recruitment days for Client Selected Candidate '] = 1
                                            else:
                                                each_record['Total No. of Recruitment days for Client Selected Candidate '] = delta.days + 1
                                        elif date1.weekday() in [5, 6] or date.weekday() in [5, 6]:
                                            each_record['Total No. of Recruitment days for Client Selected Candidate '] = delta.days + 1
                                        else:
                                            each_record['Total No. of Recruitment days for Client Selected Candidate '] = np.busday_count(date1, date) + 1
                                else:
                                    each_record['Total No. of Recruitment days for Client Selected Candidate '] = 'NA'
                        recruiter_data.append(each_record)
                    except Exception as e:
                        recruiter_data.append(each_record)
                else:
                    each_record['Project Id'] = project.id
                    each_record['Client Name'] = project.company_name
                    each_record['Role'] = project.role
                    each_record['BD Manager'] = project.bd
                    each_record['Recruiter'] = project.recruiter
                    each_record['CRM date'] = get_date_time(project.created, return_date=True)
                    # After update project details by bd project sent to recruiter admin for first pricing
                    each_record['Date sent to profile table'] = get_date_time(project.request_date, return_date=True)
                    # Pricing details
                    pricing_sent = Pricing.objects.filter(project_id=project.id)
                    pricing_length = len(list(pricing_sent))
                    if pricing_length > 0:
                        min_salary = pricing_sent[0].min_salary
                        max_salary = pricing_sent[0].max_salary
                        each_record['Candidate Proposed salary range'] = f"{min_salary} - {max_salary}"
                        each_record['Date received first candidate salary'] = get_date_time(pricing_sent[0].created)
                        each_record['Type of Payout'] = pricing_sent[0].type_of_payout
                        if pricing_length > 1:
                            each_record['Date proposed client pricing'] = get_date_time(pricing_sent[1].created)
                        if pricing_length > 2:
                            each_record['Date sent final client pricing'] = get_date_time(pricing_sent[2].created)
                        if pricing_length > 3:
                            min_salary = pricing_sent[3].min_salary
                            max_salary = pricing_sent[3].max_salary
                            each_record['Final confirmed salary range'] = f"{min_salary} - {max_salary}"
                        if pricing_length == 4:
                            # after getting proposed salary from client project assigned to recruiter
                            each_record['Date moved to recruitment after final salary'] = get_date_time(project.date_sent_to_recruitment,return_date=True)
                            if project.date_assigned_to_recruiter:
                                each_record['Date assigned to recruiter'] = get_date_time(project.date_assigned_to_recruiter, return_date=True)
                    recruiter_data.append(each_record)
            except Exception as e:
                recruiter_data.append(each_record)
        try:
            combined_data = recruiter_data
            if combined_data is not None:
                # write the data into excel sheet using dataframe
                df = pd.DataFrame(data=combined_data)
                df.index = np.arange(1, len(df) + 1)
                recruiter_file = 'All_candidates_recruitment_Dashboard_Report.xlsx' if all_candidates else 'Recruitment_Progress_Dashboard from ' + start_date + ' to ' + end_date + '.xlsx'
                df.to_excel(recruiter_file)
                template = 'recruitement_dashboard.html'
                if all_candidates:
                    context = {'title':'All candidates recruitment Dashboard Report'}
                else:
                    context = {'title': f"Recruitment Dashboard Report { start_date } to { end_date }"}
                msg_html = render_to_string(template, context)
                message = Mail(
                    from_email=FROM_EMAIL,
                    to_emails=[TO_EMAIL],
                    subject='All candidates recruitment Dashboard Report' if all_candidates else 'Recruitment_Progress_dashboard from ' + start_date + ' to ' + end_date,
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
        if all_candidates:
            context = {'title':'All candidates recruitment Dashboard Report'}
        else:
            context = {'title': f"Recruitment Dashboard Report { start_date } to { end_date }"}
        msg_html = render_to_string(template, context)
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=[TO_EMAIL],
            subject='All candidates recruitment Dashboard Report' if all_candidates else 'Recruitment_Progress_dashboard from ' + start_date + ' to ' + end_date,
            html_content=msg_html
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
