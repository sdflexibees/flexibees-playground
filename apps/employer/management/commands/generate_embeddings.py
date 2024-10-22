from django.core.management.base import BaseCommand
import datetime
from crons.generate_embeddings import generate
from apps.admin_app.views import api_logging

class Command(BaseCommand):
    help = 'python manage.py generate_embeddings'

    def handle(self, *args, **options):
        try:
            generate()
        except Exception as e:
            log_data = [f"info|| {datetime.datetime.now()}: generate embeddings command"]
            log_data.append(f"info|| {e}")
            api_logging(log_data)