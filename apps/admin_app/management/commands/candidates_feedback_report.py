from django.core.management.base import BaseCommand
from crons.candidate_feedback_report import candidate_feedback_report
import datetime
from apps.admin_app.views import api_logging


class Command(BaseCommand):
    help = 'python manage.py candidates_feedback_report'

    def handle(self, *args, **options):
        try:
            candidate_feedback_report(all_candidates=True)
            return True
        except Exception as e:
            log_data = [f"info|| {datetime.datetime.now()}: all candidates feedback report"]
            log_data.append(f"info|| {e}")
            api_logging(log_data)