import base64
import os, logging, datetime

import xlsxwriter
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import F, Q
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.timezone import now, timedelta
from sendgrid import SendGridAPIClient, FileContent, FileType, FileName, Disposition
from sendgrid.helpers.mail import Mail, Attachment

from apps.admin_app.models import Configuration, Role, Function, AdminUser
from apps.candidate.models import Shortlist, Candidate, ClientFeedback, FinalSelection, WebUser
from apps.projects.models import Project
from core.emails import email_send
from core.fcm import send_candidate_notification
from core.notification_contents import interest_check_reminder_1, interest_check_reminder_2,\
    candidate_reappear_notification, candidate_typical_day_notification_after_signup
from core.zoho import get_crm_data
from flexibees_candidate.settings import file_path, SENDGRID_API_KEY, FROM_EMAIL
from apps.projects.from_crm import has_crm_project_in_db, check_change, check_length
from apps.admin_app.views import api_logging
from flexibees_candidate.settings import FIRST_STAGE_STATUS, AVAILABILITY_REAPPEAR_REMINDER_NOTIFICATION_COUNT

def interest_check_reminder():
    response_day_1 = now() - timedelta(days=1)
    response_day_2 = now() - timedelta(days=2)
    shortlist_query_1 = Shortlist.objects.filter(active=True, status=2, project__status=8, modified__lt=response_day_1,
                                                 modified__gt=response_day_2).exclude(project__status__in=[9, 11])
    shortlist_query_2 = Shortlist.objects.filter(active=True, status=2, project__status=8, modified__lt=response_day_2) \
        .exclude(project__status__in=[9, 11])
    shortlist_1 = shortlist_query_1.values('project__role__tag_name', 'project').distinct('project')
    shortlist_2 = shortlist_query_2.values('project__role__tag_name', 'project').distinct('project')
    for shortlist in shortlist_1:
        candidates = list(shortlist_1.filter(project=shortlist['project'],
                                             candidate__hire=True).values_list('candidate__id', flat=True))
        if len(candidates) != 0:
            push_data = interest_check_reminder_1(shortlist['project'], shortlist['project__role__tag_name'])
            send_candidate_notification(candidates, push_data=push_data)
    for shortlist in shortlist_2:
        candidates = list(shortlist_2.filter(project=shortlist['project'],
                                             candidate__hire=True).values_list('candidate__id', flat=True))
        if len(candidates) != 0:
            push_data = interest_check_reminder_2(shortlist['project'], shortlist['project__role__tag_name'])
            send_candidate_notification(candidates, push_data=push_data)
    return True


def update_recruitment_day():
    Project.objects.filter(active=True, status=8).update(recruitment_days=F('recruitment_days') + 1)


def availability_reminder():
    date = now() - timedelta(days=1)
    candidates = list(Candidate.objects.filter(active=True, timeline_completed=False, questionnaire_completed=False,
                                               created__lt=date, last_login__isnull=False).values_list('id', flat=True).distinct())
    push_data = candidate_typical_day_notification_after_signup()
    send_candidate_notification(candidates, app_notify=False, push_data=push_data)
    return True


def availability_reappear_reminder():
    date = now() - timedelta(days=90)
    candidates = Candidate.objects.filter(active=True, timeline_last_updated__lt=date,
                                               mylife_last_updated__lt=date).filter(Q(last_notified__isnull=True)|Q(last_notified__lt=date))
    for candidate in candidates:
        try:
            push_data = candidate_reappear_notification(candidate.id)
            send_candidate_notification([candidate.id], push_data=push_data)
            if candidate.notification_count<AVAILABILITY_REAPPEAR_REMINDER_NOTIFICATION_COUNT:
                candidate.notification_count +=1
            if candidate.notification_count==AVAILABILITY_REAPPEAR_REMINDER_NOTIFICATION_COUNT:
                candidate.notification_count = 0
                candidate.last_notified = datetime.datetime.now()
            candidate.save()
        except Exception as e:
            log_data = [f"info|| {datetime.datetime.now()}: Exception occured while sending vailability reappear reminder"]
            log_data.append(f"info|| {candidate.id}")
            log_data.append(f"error|| {e}")
            api_logging(log_data)
    return True


def move_active_projects_to_history():
    day1 = now() - timedelta(days=2)
    day2 = now() - timedelta(days=3)
    final_selection_feedback_query = ClientFeedback.objects.filter(active=True, recommendation=3).filter(
        Q(modified__lt=day1) & Q(modified__lt=day2)).exclude(final_selection__isnull=True)
    for data in final_selection_feedback_query:
        final_selection_query = FinalSelection.objects.filter(active=True, id=data.final_selection.id)
        if final_selection_query[0].status != 6:
            final_selection_query.filter().update(status=6)
            project_obj = Project.objects.filter(id=data.final_selection.project.id, active=True, status__in=[9, 11])
            if not project_obj:
                candidate_query = get_object_or_404(Candidate, id=data.final_selection.candidate.id, active=True)
                candidate_query.active_projects -= 1 if candidate_query.active_projects != 0 else candidate_query.active_projects
                candidate_query.save()
    return True


def website_user_reminder():
    date = now() - timedelta(days=42)
    website_user_query = WebUser.objects.filter(active=True, converted=False, created__gt=date)
    subject = 'Thanks for your interest - Welcome to FlexiBees'
    template = 'website_user_email.html'
    for user in website_user_query:
        recipients = [user.email]
        context = {
            'username': user.first_name
        }
        email_send(subject, template, recipients, context)
    return True


def newly_signed_up_candidates():
    date = now() - timedelta(days=7)
    start_date = date.strftime('%d%b%Y')
    end_date = now().strftime('%d%b%Y')
    candidate_file = 'NewlySignedUpCandidates_' + start_date + '_' + end_date + '.xlsx'
    workbook = xlsxwriter.Workbook(candidate_file)
    worksheet = workbook.add_worksheet()
    bold = workbook.add_format({'bold': True})
    candidates = Candidate.objects.filter(active=True, created__gt=date).order_by('id')
    if len(candidates):
        col = 0
        row = 0
        worksheet.write(row, col, 'Candidate Id', bold) 
        worksheet.write(row, col + 1, 'First Name', bold) 
        worksheet.write(row, col + 2, 'Last Name', bold) 
        worksheet.write(row, col + 3, 'Candidate Created Time', bold) 
        worksheet.write(row, col + 4, 'Candidate Updated On', bold) 
        worksheet.write(row, col + 5, 'City', bold)
        worksheet.write(row, col + 6, 'Experience in Years', bold)
        worksheet.write(row, col + 7, 'Years of Break', bold)
        worksheet.write(row, col + 8, 'Source of FlexiBees', bold)
        worksheet.write(row, col + 9, 'Details of Source', bold)
        row += 1
        for candidate in candidates:
            worksheet.write(row, col, candidate.id)
            worksheet.write(row, col + 1, candidate.first_name)
            worksheet.write(row, col + 2, candidate.last_name)
            created = candidate.created.strftime('%d/%m/%Y %I:%M %p')
            worksheet.write(row, col + 3, created)
            modified = candidate.modified.strftime('%d/%m/%Y %I:%M %p')
            worksheet.write(row, col + 4, modified)
            worksheet.write(row, col + 5, candidate.city)
            worksheet.write(row, col + 6, candidate.total_year_of_experience)
            worksheet.write(row, col + 7, candidate.years_of_break)
            worksheet.write(row, col + 8, candidate.hear_about_flexibees)
            worksheet.write(row, col + 9, candidate.hear_about_detailed)
            row += 1
    workbook.close()
    candidates_report_file = file_path + "/" + candidate_file
    template = 'newly_added_candidates_report.html'
    context = {'title':f"Newly SignedUp Candidates from { start_date } to { end_date }"}
    msg_html = render_to_string(template, context)
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=['rashmi@flexibees.com'],
        #to_emails=['kiran@appinessworld.com'],
        subject='Newly SignedUp Candidates from ' + start_date + ' to ' + end_date,
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
    return True


def pull_data_from_crm(all_records=False):
    log_data = []
    try:
        log_data.append(f"info|| {datetime.datetime.now()}: pull_from_crm")
        pulled_data = get_crm_data(all=all_records)
        log_data.append(f"info|| Total records received from crm: {len(pulled_data)}")
        log_data.append(f"info|| {datetime.datetime.now()}: pull_from_crm")
        bulk_data = []
        duplicates =[]
        existing_records = list(Project.objects.all().order_by('zoho_id').values())
        bd_managers = AdminUser.objects.filter(roles__contains=['bd']).values('id', 'email')
        roles = Role.objects.all()
        all_role_types = []
        all_model_types = []
        try:
            all_role_types = list(Configuration.objects.get(dropdown__key_name='role_type').tags.all().
                                values_list('name', flat=True))
        except ObjectDoesNotExist as e:
            log_data.append("error|| error from all role types")
            log_data.append(f"info|| {e}")
        try:
            all_model_types = list(Configuration.objects.get(dropdown__key_name='model_type').tags.all().
                                values_list('name', flat=True))
        except ObjectDoesNotExist as e: 
            log_data.append("error|| error from all model types")
            log_data.append(f"info|| {e}")

        for each_data in pulled_data:
            if each_data['id']  in duplicates:
                continue
            bd_id = None
            try:
                for bd in bd_managers:
                    if str.lower(each_data['Owner']['email']) == str.lower(bd['email']):
                        bd_id = bd['id']
                        break
            except Exception:
                pass
            # get the project from database if exists.
            project = has_crm_project_in_db(existing_records,  str(each_data['id']))
            # if project exists and if bd email exists in zoho and if email which is there in our db is not equal to the incoming email from zoho, update the email irrespective of the stages.
            if project and each_data ['Owner']['email'] and project['bd_email'].strip().lower() != each_data ['Owner']['email'].strip().lower():
                bd = AdminUser.objects.filter(email=each_data ['Owner']['email']).first()
                # update the bd manager email and bd instance. 
                Project.objects.filter(id=project['id']).update(bd_email=each_data ['Owner']['email'], bd=bd)
            # if the incoming project is not there in the below mentioned stages don't allow that project to create or update.
            if str(each_data.get('Stage', '') or '') not in ['Information', 'Profile Creation', 'Proposal Creation',
                                                            'Profile Sent', 'Proposal Sent', 'Negotiation',
                                                            'Proposal Closed']:
                continue
            if not project :
                try:
                    if str.lower(each_data['Functional_Requirement']) == 'content':
                        form_type = 'content'
                    elif str.lower(each_data['Functional_Requirement']) == 'sales/ bd':
                        form_type = 'sales'
                    else:
                        form_type = 'general'
                    role = each_data.get('Role_Requirement')
                    role_obj = None
                    role_type = ''
                    model_type = ''
                    role_lower = each_data['Wanted_Office_Travel'].lower()
                    for each_role_type in all_role_types:
                        if role_lower == each_role_type.lower():
                            role_type = each_role_type
                            break
                    model_lower = each_data['Wanted_Full_time'].lower()
                    for each_model_type in all_model_types:
                        if model_lower  == each_model_type.lower():
                            model_type = each_model_type
                            break
                    try:
                        if role is not None:
                            role_obj = Role.objects.get(tag_name__iexact=role)
                    except ObjectDoesNotExist as e:
                        log_data.append("error|| Role object does not exist")
                        log_data.append(f"info|| {role}")
                        log_data.append(f"info|| {e}")

                    if check_length(each_data, role_type, model_type, api_logging) :
                        bulk_data.append(Project(zoho_id=each_data['id'], deal_name=each_data['Deal_Name'],
                                            bd_email=each_data['Owner']['email'],
                                            bd_id=bd_id,
                                            company_name=each_data['Account_Name']['name'],
                                            contact_name=each_data['Contact_Name']['name'],
                                            function=Function.objects.get(tag_name__iexact=each_data['Functional_Requirement']),
                                            role=role_obj,
                                            role_type=role_type,
                                            model_type=model_type,
                                            description=str(each_data.get('Description', '') or ''),
                                            flex_details=str(each_data.get('Pricing_Expectation_was_Lower_than_Ours', '') or ''),
                                            stage=str(each_data.get('Stage', '') or ''),
                                            next_step=str(each_data.get('Next_Steps', '') or ''),
                                            status_description=str(each_data.get('Description', '') or ''),
                                                form_type=form_type
                                            ))
            
                        duplicates.append(each_data['id'])
                except Exception as e:
                    log_data.append(f"error|| error occured while creating new project {each_data['id']}")
                    log_data.append(f"info|| {e}")
            elif project['status'] == FIRST_STAGE_STATUS:
                role = each_data.get('Role_Requirement')
                role_obj = None
                role_type = ''
                model_type = ''
                lower_role = each_data['Wanted_Office_Travel'].lower()
                for each_role_type in all_role_types:
                    if lower_role == each_role_type.lower() :
                        role_type = each_role_type
                        break
                lower_model = each_data['Wanted_Full_time'].lower()
                for each_model_type in all_model_types:
                    if lower_model == each_model_type.lower():
                        model_type = each_model_type
                        break
                
                if role is not None:
                    lower_case_role = role.lower()
                    for obj in roles:
                        if obj.tag_name.lower() == lower_case_role:
                            role_obj = obj
                
                try:
                    if not check_change(project,each_data,role_type, model_type,role_obj.id if role_obj else role_obj) and check_length(each_data,role_type,model_type,api_logging):
                        project_query = Project.objects.get(zoho_id=each_data['id'])
                        project_query.deal_name = each_data['Deal_Name']
                        project_query.company_name = each_data['Account_Name']['name']
                        project_query.contact_name = each_data['Contact_Name']['name']
                        project_query.role = role_obj
                        project_query.role_type = role_type
                        project_query.model_type = model_type
                        project_query.flex_details = str(each_data.get('Pricing_Expectation_was_Lower_than_Ours', '') or '')
                        project_query.stage = str(each_data.get('Stage', '') or '')
                        project_query.next_step = str(each_data.get('Next_Steps', '') or '')
                        project_query.status_description = str(each_data.get('Description', '') or '')
                        project_query.save()
                except Exception as e:
                    log_data.append(f"error|| error occured while updating {project['zoho_id']}")
                    log_data.append(f"info|| {e}")
            log_data.append("info|| Iteration completed")
            log_data.append(f"info|| {'-'*100}")
        Project.objects.bulk_create(bulk_data)
        api_logging(log_data)
        return True
    except Exception as e:
        log_data = [f"info|| {datetime.datetime.now()}: pull_from_crm"]
        log_data.append(f"error|| {e}")
        api_logging(log_data)
