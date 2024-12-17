import json
from django.core.management.base import BaseCommand
import datetime
from apps.admin_app.views import api_logging
from apps.admin_app.models import City, Country


class Command(BaseCommand):
    help = 'python manage.py add_cities'

    def handle(self, *args, **options):
        try:
            with open('country_cities.json', 'r') as cc_file:
                cities_data = json.load(cc_file)
                for country in cities_data:
                    if country['cities']:
                        country_obj = Country(
                            name=country['name']
                        )
                        country_obj.save()
                        city_objs = [
                            City(
                                name=city['name'],
                                country=country_obj
                            )
                            for city in country['cities']
                        ]
                        City.objects.bulk_create(city_objs)
            # return True
            self.stdout.write(self.style.SUCCESS('Cities and countries successfully added.'))
        except Exception as e:
            log_data = [f"info|| {datetime.datetime.now()}: add cities function"]
            log_data.append(f"info|| {e}")
            api_logging(log_data)
            # return False
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))
        