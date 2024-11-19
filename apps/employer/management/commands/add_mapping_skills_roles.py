from django.core.management.base import BaseCommand
import datetime
from scripts.mapping_script_role_skill import mapping_conversion
from apps.admin_app.views import api_logging
from flexibees_finance.settings.base import file_path
import os

class Command(BaseCommand):
    help = 'python manage.py add_mapping_skills_roles'
    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='The path to the input file')
      
    def handle(self, *args, **options):
        message = "mapping process started successfully "
        self.stdout.write(message)
        try:
            input_file_path = options['file_path']
            if os.path.exists(input_file_path):
                path_info = os.path.join(file_path,"data")
                if os.path.exists(path_info) == False:
                    os.makedirs(path_info)
                output_path_info = os.path.join(path_info,"output_storage")
                if os.path.exists(output_path_info) == False:
                    os.makedirs(output_path_info)     
                file_name = "output_file_"+(str(datetime.datetime.now())).replace(" ","_")+".xlsx"
                output_file_path=mapping_conversion(input_file_path,output_path_info,file_name)
                print("Output Log file path :  ", output_file_path)
            else:
                print("Provided file path doesn't exist please retry again")
            print("mapping process ending successfully")
        except Exception as e:
            log_data = [f"info|| {datetime.datetime.now()}: add cities function"]
            log_data.append(f"info|| {e}")
            api_logging(log_data)