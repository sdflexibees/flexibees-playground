import os
import csv
import logging
import xlsxwriter
import base64
from tqdm import tqdm
from datetime import datetime
from apps.availability.views import get_question_key
from apps.candidate.serializers import get_profile_percentage
from apps.candidate.models import Candidate, CandidateAttachment, CandidateLanguage, Certification, Education, EmploymentDetail
from django.utils.timezone import now, timedelta
from flexibees_finance.settings import file_path, SENDGRID_API_KEY, FROM_EMAIL
from django.template.loader import render_to_string
from sendgrid import SendGridAPIClient, FileContent, FileType, FileName, Disposition
from sendgrid.helpers.mail import Mail, Attachment
from apps.admin_app.views import api_logging


"""
    -> Please Ensure the first row sheet is a "Headings Row".
    -> TQDM liberary is used to show progress bar in Console

    Steps to Run the Script:
    1. Open django Shell :- 
        python manage.py shell
    2. import the file:-
        from scripts.on_demand_task import On_Demand_Task as od
    3. Call the function with file name :- 
        od('DigitalUsersList.csv')
"""


# Main Function
def On_Demand_Task(file_name):
    try:
        # To log the execution time
        start_time = datetime.now()

        # Create Log file:
        log_dir = f'{os.getcwd()}/scripts/logs'
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        logging.basicConfig(
            filename=f'{log_dir}/On_Demand_Task_{datetime.now().date()}.log', level=logging.DEBUG)

        logging.info(datetime.now())
        logging.info("Task Started")

        # File used in Script
        files_to_process = ['DigitalUsersList.csv', 'SalesUsersList.csv']

        # Fetch all documents with full path.
        document_dir = f"{os.getcwd()}/scripts/documents"

        logging.info(f"File name given in Command Line: {file_name}")

        # Check file_name is present in processed file list or not
        if file_name in files_to_process:
            filepath = f"{document_dir}/{file_name}"
            print(f"\nProcessed file name: {file_name}\n")

            # Proceed with the document
            process_the_document(filepath, file_name)
        else:
            print(
                f"\nFile not exist. Check the Document folder if file exist or not and file name is as same as mentioned :{files_to_process}")
            logging.info(
                f"File not exist. Check the Document folder if file exist or not and file name is as same as mentioned :{files_to_process}")

    except Exception as e:
        logging.error(f'Main Function: {str(e)}')

    logging.info("Task Ran Successfully")

    # To log the execution time
    end_time = datetime.now()
    logging.info(
        f"Execution time(hh:mm:ss): {(end_time - start_time)}")
    print("Ran Successfully")
    return True


def process_the_document(filepath, file_name):
    try:
        # Variable used in function
        not_found = "NA"
        output_file_data_list = []
        not_existing_email = []

        logging.info(f"Processed file name: {file_name}")

        # Reading a csv file in list of Dictionary (rows in csv/xlxs..)
        reader = list(csv.DictReader(open(filepath)))

        # Fetch extra details and add it in a output file list
        if len(reader) > 1:
            for row in tqdm(reader):
                # Add additional Detail Keys in a row data with "NA"
                row['Signed Up/ Logged In on App?'] = not_found
                row['Profile Completion Rate'] = not_found
                row['Mobile(In App)'] = not_found
                row['City(In App)'] = not_found
                row['Profile Pic'] = not_found
                row['Profile Summary'] = not_found
                row['Skills'] = not_found
                row['Employment Detail'] = not_found
                row['Education'] = not_found
                row['Certification'] = not_found
                row['Candidate Language'] = not_found
                row['Candidate Attachment'] = not_found
                row['Portfolio Link'] = not_found
                row['My Life Section Filled?'] = not_found
                row['My Day Section Filled?'] = not_found

                # Updating the List
                output_file_data_list.append(
                    get_candidate_details(
                        row['Email'].strip(), row, not_existing_email)
                )

            # writing to output csv file
            # Headers for Output File
            headers_for_csv = output_file_data_list[0].keys()
            # Get the Output file Name with output path
            """
                if Input File name is:
                    "Digital.csv"

                Output File name be like this:
                    "Digital-20-Aug-2022.csv"
            """
            processed_file_dir = f"{os.getcwd()}/scripts/processed_documents"
            if not os.path.exists(processed_file_dir):
                os.makedirs(processed_file_dir)
            before_processed_file_name, extension = file_name.split('.')

            after_processed_file_name = f"{before_processed_file_name}-{datetime.now().strftime('%d-%b-%Y')}.{extension}"
            after_processed_full_filepath = f"{processed_file_dir}/{after_processed_file_name}"

            # creating a csv dict writer object
            writer = csv.DictWriter(
                open(after_processed_full_filepath, 'w'), fieldnames=headers_for_csv)

            # writing headers (field names)
            writer.writeheader()

            # writing data rows
            writer.writerows(output_file_data_list)

            logging.info(f"These Emails are not exist: {not_existing_email}")
    except Exception as e:
        logging.error(f'Process The Document Function: {str(e)}')
    return True


def get_candidate_details(candidate_email, row, not_existing_email):
    """
        Get all Details of Candidate
    """
    try:
        candidate_obj = Candidate.objects.get(email=candidate_email.lower())
        skills = list(candidate_obj.skills.all().values_list(
            "tag_name", flat=True
        ))
        employment_detail = list(EmploymentDetail.objects.filter(
            candidate=candidate_obj).values(
                "company",
                "currently_working",
                "start_date",
                "end_date"
        ))
        education = list(Education.objects.filter(
            candidate=candidate_obj).values(
                "school_college",
                "education",
                "course",
                "field_of_study",
                "grade",
                "start_date",
                "end_date"
        ))
        certification = list(Certification.objects.filter(
            candidate=candidate_obj).values(
                "title",
                "issued_by",
                "issue_date"
        ))
        candidate_language = list(CandidateLanguage.objects.filter(
            candidate=candidate_obj).values(
                "language__name",
                "proficiency",
                "read",
                "write",
                "speak"
        ))
        candidate_attachment = list(CandidateAttachment.objects.filter(
            candidate=candidate_obj).values(
                "title",
                "attachment"
        ))
        row['Signed Up/ Logged In on App?'] = "Yes" if candidate_obj.active else "No"
        row['Profile Completion Rate'] = get_profile_percentage(candidate_obj)
        row['Mobile(In App)'] = candidate_obj.phone
        row['City(In App)'] = candidate_obj.city
        row['Profile Pic'] = candidate_obj.profile_pic
        row['Profile Summary'] = candidate_obj.profile_summary
        row['Skills'] = skills or ''
        row['Employment Detail'] = employment_detail or ''
        row['Education'] = education or ''
        row['Certification'] = certification or ''
        row['Candidate Language'] = candidate_language or ''
        row['Candidate Attachment'] = 'Yes' if candidate_attachment else 'No'
        row['Portfolio Link'] = 'Yes' if candidate_obj.portfolio_link else 'No'
        row['My Life Section Filled?'] = get_mylife_status(candidate_obj)
        row['My Day Section Filled?'] = get_myday_status(candidate_obj)
    except Exception as e:
        not_existing_email.append(candidate_email)
        logging.error(
            f'Get Candidate Function: {candidate_email}: {str(e)}')
    return row


def get_mylife_status(candidate_obj):
    """
        We have 4 Question:
        3 Independent Question
        1 Dependent Question
        -> Question number 1, 2 and 4 is Independent Question.
        -> Question '4' is mandatory Question to answer(Last Question).
        -> Question '3' is depend on Question '2' answer(candidate may be answer may be not).

        So,
        -> "Yes": if these 3 questions(1,2,4) are present in Candidate Lifestyle Response(Means he answered all Question).
        -> "No": if these 3 question is not present in Candidate Lifestyle Response
    """

    candidate_answers_list = candidate_obj.lifestyle_responses

    # Remove None from Candidate Lifestyle Response List(is present)
    if None in candidate_answers_list:
        candidate_answers_list = list(
            filter(lambda item: item is not None, candidate_answers_list))

    # Sorting candidate answer choice in ascending order(based on questions)
    candidate_answers_list.sort(key=get_question_key)

    # Get the Question answered by Candidate
    questions_answered_by_candidate = list(
        map(get_question_key, candidate_answers_list))

    # Checking the Mandatory Question were answered or not
    if {'1', '2', '4'}.issubset(set(questions_answered_by_candidate)):
        return "Yes"
    return f"No {questions_answered_by_candidate or ''}"


def get_myday_status(candidate_obj):
    """
    -> We have Two Field in Candidate Table
        a. wakeup_time (If Candidate starts filling the Typical day section, then the values of this field in db is not None(Null))
        b. timeline_completed (if Candidate Completely filled his Typical day Section, then the value of this field in db is 'True' else 'False')

        Based on this we can set the Status.
        1. "Not Started"
        2. "Started not completed"
        3. "Completed"
    """
    wakeup_time = candidate_obj.wakeup_time
    timeline_completed = candidate_obj.timeline_completed
    if wakeup_time and timeline_completed:
        return "Completed"
    elif wakeup_time and timeline_completed is False:
        return "Started not completed"
    else:
        return "Not Started"

def all_signed_up_candidates_report():
    try:
        candidate_file = 'AllSignedUpCandidates.xlsx'
        workbook = xlsxwriter.Workbook(candidate_file)
        worksheet = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True})
        candidates = Candidate.objects.filter(active=True).order_by('id')
        if len(candidates)>0:
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
            for index, candidate in enumerate(candidates):
                row = index+1
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
            workbook.close()
            try:   
                template = 'newly_added_candidates_report.html'
                context = {'title':'All SignedUp Candidates'}
                msg_html = render_to_string(template, context)
                message = Mail(
                    from_email=FROM_EMAIL,
                    to_emails=['rashmi@flexibees.com'],
                    # to_emails=['naveen.v@appinessworld.com'],
                    subject='All SignedUp Candidates',
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
                log_data = [f"info|| {datetime.now()}: Exception occured in all candidates signUp report script"]
                log_data.append(f"error|| {e}")
                api_logging(log_data)
                os.unlink(candidate_file)
                return False
        return True
    except Exception as e:
        log_data = [f"info|| {datetime.now()}: Exception occured in all candidates signUp report script"]
        log_data.append(f"error|| {e}")
        api_logging(log_data)
        return False

