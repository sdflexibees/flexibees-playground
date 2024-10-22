import logging
import base64
import os
import time
import pytz
from sendgrid.helpers.mail import Mail, Attachment
from django.core.paginator import Paginator
from flexibees_candidate.settings import SENDGRID_API_KEY, FROM_EMAIL
from django.template.loader import render_to_string
from apps.candidate.models import ClientFeedback
from apps.projects.models import Project, Pricing
from sendgrid import SendGridAPIClient, FileContent, FileType, FileName, Disposition
import pandas as pd
import numpy as np


def get_date_time(dt, return_date=False):
    if dt is None:
        return ""
    date_fmt = "%d-%m-%Y"
    dt_fmt = "%d-%m-%Y  %H:%M:%S"
    return dt.astimezone(pytz.timezone('Asia/Kolkata')).strftime(date_fmt if return_date else dt_fmt)


def common_data(each_record,project):
    each_record['Client Name'] = project.deal_name
    each_record['Role'] = project.role
    each_record['BD Manager'] = project.bd
    each_record['Recruiter'] = project.recruiter
    each_record['CRM date'] = get_date_time(project.created, return_date=True)
    # After update project details project sent to recruiter admin
    each_record['Date sent to recruitment'] = get_date_time(project.request_date,
                                                            return_date=True)
    # Pricing details
    pricing_sent = project.pricing_set.get(project_id=project.id, stage=1)
    min_salary = pricing_sent.min_salary
    max_salary = pricing_sent.max_salary
    each_record['Candidate Proposed salary range'] = f"{min_salary} - {max_salary}"
    each_record['Date sent requesting candidate Salary'] = get_date_time(pricing_sent.created)
    pricing_recieve = project.pricing_set.get(project_id=project.id, stage=4)
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
        each_record['Number of selected candidate'] = project.client_selected
    else:
        each_record['selected'] = 'No'
        each_record['Number of selected candidate'] = 0


def recruitment_progress_dashboard():
    recruiter_data = []
    project_query = Project.objects.prefetch_related('finalselection_set', 'pricing_set').distinct()
    # giving the number of records to be sliced at once
    page_size = 3000
    page_no = 1
    # getting the records in a page according to page_size
    pages = Paginator(project_query, page_size)
    ids_list = set()
    while page_no <= pages.num_pages:
        # assigning the number of records to be checked at once
        project_query = pages.get_page(page_no)
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
                               'Candidate Proposed salary range': '',
                               'Final confirmed salary range': '',
                               'Type of Payout':'',
                               'Total No. of Recruitment Days for First Final Selection ': '',
                               'Total No. of Recruitment days for Client Selected Candidate ': ''}
                final_candidate = project.finalselection_set.filter(project_id=project.id)
                if len(final_candidate) > 0:
                    for final in final_candidate:
                        # removing duplicate data
                        if project.id in ids_list:
                            continue
                        ids_list.add(project.id)
                        try:
                            each_record['First time a candidate moves to every new stage'] = get_date_time(final.created, return_date=True)
                            common_data(each_record,project)
                            each_record['First final candidate profile sent to BD manager'] = get_date_time(project.send_to_bdmanager, return_date=True)
                            client_fb = ClientFeedback.objects.filter(final_selection_id=final.id).first()
                            if client_fb is not None:
                                each_record['Date of client feedback/ Candidate selected'] = get_date_time(client_fb.created, return_date=True)
                                each_record['Date of Candidate selected'] = get_date_time(client_fb.created, return_date=True)
                            # after getting proposed salary from client project assigned to recruiter
                            each_record['Assigned to recruiter'] = get_date_time(project.date_sent_to_recruitment,return_date=True)
                            date1 = project.date_sent_to_recruitment.date()
                            date2 = project.send_to_bdmanager.date()
                            delta = date2 - date1
                            if date1.weekday() in [5, 6] and date2.weekday() in [5, 6]:
                                if date1 == date2:
                                    each_record['Total No. of Recruitment Days for First Final Selection '] = 1
                                else:
                                    each_record[
                                        'Total No. of Recruitment Days for First Final Selection '] = delta.days + 1
                            elif date1.weekday() in [5, 6] or date2.weekday() in [5, 6]:
                                each_record['Total No. of Recruitment Days for First Final Selection '] = delta.days + 1
                            else:
                                each_record['Total No. of Recruitment Days for First Final Selection '] = np.busday_count(date1,date2) + 1
                            first_client_selected = ClientFeedback.objects.filter(final_selection__project_id=project.id, recommendation__in=[3, 5]).order_by('created').first()
                            if first_client_selected is not None:
                                send_to_bdmanager = first_client_selected.final_selection.send_to_bdmanager
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
                        except:
                            recruiter_data.append(each_record)
                            continue
                else:
                    common_data(each_record,project)
                    each_record['Assigned to recruiter'] = get_date_time(project.date_sent_to_recruitment, return_date=True)
                    date1 = project.date_sent_to_recruitment.date()
                    date2 = project.send_to_bdmanager.date()
                    delta = date2 - date1
                    if date1.weekday() in [5, 6] and date2.weekday() in [5, 6]:
                        if date1 == date2:
                            each_record['Total No. of Recruitment Days for First Final Selection '] = 1
                        else:
                            each_record[
                                'Total No. of Recruitment Days for First Final Selection '] = delta.days + 1
                    elif date1.weekday() in [5, 6] or date2.weekday() in [5, 6]:
                        each_record['Total No. of Recruitment Days for First Final Selection '] = delta.days + 1
                    else:
                        each_record['Total No. of Recruitment Days for First Final Selection '] = np.busday_count(date1,date2) + 1
                    recruiter_data.append(each_record)
            except Exception as e:
                recruiter_data.append(each_record)
                continue
        # increasing the page number to process the remaining records
        page_no += 1
        # setting the process to sleep for 2 seconds so that it takes time and the remaining process also will keep running
        time.sleep(2)
    try:
        if recruiter_data is not None:
            # write the data into excel sheet using dataframe
            df = pd.DataFrame(data=recruiter_data)
            df.index = np.arange(1, len(df) + 1)
            recruiter_file = 'Recruitment_Progress_Dashboard.xlsx'
            df.to_excel(recruiter_file)
            template = 'recruitement_dashboard.html'
            msg_html = render_to_string(template)
            message = Mail(
                from_email=FROM_EMAIL,
                to_emails=['rashmi@flexibees.com'],
                # to_emails=['girish@appinessworld.com','gurusharan@appinessworld.com','kiran@appinessworld.com'],
                subject='Recruitment_Progress_dashboard',
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
        msg_html = render_to_string(template)
        message = Mail(
            from_email=FROM_EMAIL,
            to_emails=['rashmi@flexibees.com'],
            # to_emails=['girish@appinessworld.com', 'gurusharan@appinessworld.com', 'kiran@appinessworld.com'],
            subject='Recruitment_Progress_dashboard',
            html_content=msg_html
        )
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)



