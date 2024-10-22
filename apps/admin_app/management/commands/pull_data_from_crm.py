from django.core.management.base import BaseCommand
from core.crons import pull_data_from_crm
import datetime
from apps.admin_app.views import api_logging


class Command(BaseCommand):
    help = 'python manage.py pull_data_from_crm'

    def handle(self, *args, **options):
        try:
            pull_data_from_crm(True)
            return True
        except Exception as e:
            log_data = [f"info|| {datetime.datetime.now()}: all candidates feedback report"]
            log_data.append(f"info|| {e}")
            api_logging(log_data)