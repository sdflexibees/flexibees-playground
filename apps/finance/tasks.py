# from celery import shared_task
# from celery.utils.log import get_task_logger
# from django.core.mail import EmailMultiAlternatives


# logger = get_task_logger(__name__)


# @shared_task(name='send_email_contract')
# def send_mail_contract(subject, plain_message, html_message, from_email, to_email, contract_filename, contract_pdf_content):
#     try:
#         email = EmailMultiAlternatives(subject, plain_message, from_email, [to_email])
#         email.attach(contract_filename, contract_pdf_content, 'application/pdf')
#         email.attach_alternative(html_message, "text/html")
#         email.send()
#         return {"status": "true", "message": "Email sent successfully"}
#     except Exception as e:
#         logger.error(f"Error sending email: {e}")
#         return {"status": "false", "message": "Error sending email"}