import base64
from sendgrid.helpers.mail import Mail, Attachment
from flexibees_finance.settings import file_path, SENDGRID_API_KEY, FROM_EMAIL
from django.template.loader import render_to_string
from apps.candidate.models import Candidate, ClientFeedback, FinalSelection, Flexifit,CandidateAttachment
from sendgrid import SendGridAPIClient, FileContent, FileType, FileName, Disposition
import pandas as pd
import numpy as np
from urllib.parse import urlparse
from pyresparser import ResumeParser
import wget
import os
import logging
import nltk
from apps.admin_app.models import Skill
nltk.download('stopwords')

def resume_skills_export():
    candidate_attach=CandidateAttachment.objects.filter().values_list('attachment','candidate_id').order_by('-id')
    total_count = len(candidate_attach)
    invalid_files=[]
    if candidate_attach is not None:
        for file_path in candidate_attach:
            invalid_user = {'candidate_id': '', 'candidate_name': '', 'Email': '', 'Phone_no': ''}
            try:
                candidate = Candidate.objects.get(id=file_path[1])
                URL = file_path[0]
                path = urlparse(URL).path
                ext = os.path.splitext(path)[1]
                if URL:
                    if ext=='.pdf' or ext=='.docx' or ext=='.doc':
                        file='sample'+ext
                        wget.download(URL,f"./resume/{file}")
                        try:
                            data = ResumeParser(f"./resume/{file}",skills_file='skills.csv').get_extracted_data()
                            if candidate is not None:
                                candidate.skills_resume=data['skills']
                                candidate.save()
                        except:
                            pass
                    else:
                        invalid_user['candidate_id']=candidate.id
                        invalid_user['candidate_name'] = candidate.first_name
                        invalid_user['Email'] = candidate.email
                        invalid_user['Phone_no'] = candidate.phone
                        if candidate.id not in invalid_files:
                            invalid_files.append(invalid_user)
                    os.remove(f"./resume/{file}")
                total_count = total_count - 1
                print('******Total Count Reaminig******',total_count)
            except Exception as e:
                logging.error(f'Error{str(e)}')
                continue
    if invalid_files:
        try:
            df = pd.DataFrame(data=invalid_files)
            df.index = np.arange(1, len(df) + 1)
            candidate_file = 'invalid_files'+ '.xlsx'
            df.to_excel(candidate_file)
            template = 'candidate_feedback_report.html'
            context = {'data':'invalid user'}
            msg_html = render_to_string(template, context)
            message = Mail(
                from_email=FROM_EMAIL,
                # to_emails=['rashmi@flexibees.com'],
                to_emails=['kiran@appinessworld.com'],
                subject='invalid user',
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

def skills_list():
    """
    Updating the skills from
    skills table to skills.csv
    :return:
    """
    try:
        skills = Skill.objects.all().values_list('tag_name', flat=True)
        if skills:
            with open("skills.csv", 'a') as f:
                for skill in skills:
                    f.write(',' + skill.title() + ',' + skill.lower())
    except Exception as e:
        logging.error(f'unable to fetch skill : Error{str(e)}')


