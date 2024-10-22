from django.core.management.base import BaseCommand, CommandError

from scripts.on_demand_task import On_Demand_Task


class Command(BaseCommand):
    help = 'This command is used to process Digital and Sales Sheets, Options are "DigitalUsersList.csv" and "SalesUsersList.csv"'

    def add_arguments(self, parser):
        parser.add_argument('file_name', type=str)

    def handle(self, **kwargs):
        try:
            # Calling the File processing function to process the files.
            On_Demand_Task(kwargs['file_name'])
            
            # At the end of the function giving a success message
            self.stdout.write(self.style.SUCCESS("Command ran successfully"))
        except Exception as e:
            raise CommandError(f'Command Error: {e}')
