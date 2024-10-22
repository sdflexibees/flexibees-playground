from django.core.management.base import BaseCommand
from crons.recruitment_dashboard_weekly_report import recruitment_progress_dashboard
import datetime
from apps.admin_app.views import api_logging


class Command(BaseCommand):
    help = 'python manage.py recruitment_dashboard_report'

    def handle(self, *args, **options):
        try:
            recruitment_progress_dashboard(all_candidates=True)
            return True
        except Exception as e:
            log_data = [f"info|| {datetime.datetime.now()}: all candidates recruitment dashboard report"]
            log_data.append(f"info|| {e}")
            api_logging(log_data)
            

