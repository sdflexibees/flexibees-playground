from apps.employer.constants import (CONVERSION_VALUES_USD, YEARS, MONTHLY, WEEKS, DAYS, 
                                DEFAULT_ADDITIONAL_AMOUNT, DEFAULT_CURRENCY, MINIMUM_DEFAULT_RATIO_PRICING,
                                DURATION, CURRENCY_FORMAT)
from apps.employer.models import  CustomRole, RolesMinMaxPricing
from apps.admin_app.models import Role
from apps.common.models import RoleMapping
from apps.common.constants import PENDING_STATUS
from apps.projects.models import Project, Pricing
from datetime import timedelta
from django.utils import timezone
from apps.admin_app.views import api_logging
from datetime import datetime
from scripts.openai_scripts import AIServiceWrapperIntegration
import requests
import json

class CandidatePricingAlgorithm :

    def currency_conversion(self, amount, currency_type):
        """
        Converting the amount into United State Doller Format Which is default constent.

        Parameters:
        amount (float): The amount in number.
        currency_type (str): The target currency type for conversion. Must be one of the keys in CONVERSION_VALUES_USD. ilke , INR , USD , SDG , SGD

        Returns:
        float: The converted amount in the default United State Doller currency.

        Raises:
        KeyError: If the specified currency_type is not found in CONVERSION_VALUES_USD.
        ValueError: If the conversion value for the specified currency_type is not a valid float.

        Example:
        >>> conversion = currency_conversion(100, 'INR')
        1.2  # Assuming the conversion rate for INR is ( $ 0.012 )
        """
        log_data = [f"info|| {datetime.now()}: Exception occured  while coversion of amount {amount} with currency type {currency_type}"]
        res =0
        try:
            res = float(amount) * float(CONVERSION_VALUES_USD[currency_type])
        except Exception  as x :
            log_data.append(f"error|| {str(x)}")
            api_logging(log_data)
        return res
    def conversion_of_day_in_hour(self, project_duration_unit , project_duration):
        """
        Converts the project duration into working hours based on the specified unit of time.

        Args:
            project_duration_unit (str): The unit of time for the project duration. 
                                        Can be 'YEARS', 'MONTHLY', 'WEEKS', or 'DAYS'.
            project_duration (int): The duration of the project in the specified unit of time.

        Returns:
            int: The project duration converted into working hours.
        """

        if project_duration_unit == YEARS:
            # Converting project duration from years to number of days
            number_of_days = project_duration * 360
            # Converting total days into number of working days
            number_of_working_days = number_of_days // 5
            # Multiplying number of working days by 8 hours per workday
            morking_into_working_hour = number_of_working_days * 8
            return morking_into_working_hour, True

        if project_duration_unit == MONTHLY:
            # Converting project duration from years to number of days
            number_of_days = project_duration * 30
            # Converting total days into number of working days
            number_of_working_days = number_of_days // 5
            # Multiplying number of working days by 8 hours per workday
            morking_into_working_hour = number_of_working_days * 8
            return morking_into_working_hour, True
        
        if project_duration_unit == WEEKS:
            # Converting project duration from years to number of days
            number_of_days = project_duration * 7
            # Converting total days into number of working days
            number_of_working_days = number_of_days - (project_duration * 2)
            # Multiplying number of working days by 8 hours per workday
            morking_into_working_hour = number_of_working_days * 8
            return morking_into_working_hour, True
        
        if project_duration_unit == DAYS:
            # Multiplying number of working days by 8 hours per workday
            morking_into_working_hour = project_duration * 8
            return morking_into_working_hour, True
        return None, False

    
    def arrange_date_format(self, pricing_values, function_name, role_name):
        """
        Filters pricing values based on their modified dates into three distinct periods:
        from today to 3 months ago, from 3 months ago to 6 months ago, and from 6 months ago to 1 year ago.
        If no data is found for the first period, it checks the next period, and so on.
        If no data is found in any period, it defaults to returning all the pricing values.

        Parameters:
            pricing_values (QuerySet): A Django QuerySet of pricing values to be filtered based on their modified dates.

        Returns:
        QuerySet: A filtered QuerySet of pricing values based on the defined periods.
                If no data is found in any period, returns data from OPEN Ai (Have to Implment it)
        """
        log_data = [f"info|| {datetime.now()}: Exception occured  while arranging data in format"]
        try:
            today_date = timezone.now()
            three_months_ago = today_date - timedelta(days=90)

            # filtering based on modified date today month to 3 month  ago
            pricing_values_3_month = list(pricing_values.filter(modified__gte=three_months_ago, modified__lte=today_date))

            if pricing_values_3_month  and len(pricing_values_3_month) >= MINIMUM_DEFAULT_RATIO_PRICING:
                return pricing_values_3_month
            six_months_ago = today_date - timedelta(days=180)

            # filtering based on modified date 3 month to 6 month  ago
            pricing_values_6_month = list(pricing_values.filter(modified__gte=six_months_ago, modified__lte=three_months_ago))

            # Checking if 3 month data and 6 month data is available after concatenating with 3 month is above then 10 send other wise go for 6 month data .
            
            three_and_six_month_data = (pricing_values_3_month+pricing_values_6_month)[:10]
            if len(three_and_six_month_data) >= MINIMUM_DEFAULT_RATIO_PRICING:
                return three_and_six_month_data
            
            if pricing_values_6_month and len(pricing_values_6_month) >= MINIMUM_DEFAULT_RATIO_PRICING:
                return pricing_values_6_month

            # filtering based on modified date 6 month to 12 month  ago
            one_year_ago = today_date - timedelta(days=365)
            pricing_values_12_month = list(pricing_values.filter(modified__gte=one_year_ago, modified__lte=six_months_ago))

            # Checking if 6 month data and 12 month data is available after concatenating with 6 month is above then 10 send other wise go for 12 month data .

            six_and_twelve_month_data = (three_and_six_month_data+pricing_values_12_month)[:10]
            if len(six_and_twelve_month_data) >= MINIMUM_DEFAULT_RATIO_PRICING:
                return six_and_twelve_month_data

            if pricing_values_12_month and len(pricing_values_12_month) >= MINIMUM_DEFAULT_RATIO_PRICING:
                return pricing_values_12_month
            
            # Have fetch data from OPEN AI
            chatgpt_model = AIServiceWrapperIntegration()
            pricing_values = chatgpt_model.pricing_data_fetched(function_name, role_name)

            if pricing_values[0]:
                return pricing_values[-1]
            return []            
        except Exception  as x :
            log_data.append(f"error|| {str(x)}")
            api_logging(log_data)
            return pricing_values

    def median_of_list(self, lst):
        """
        Calculate the median of a list of numeric strings.

        Args:
            lst (list of str): List containing numeric strings.
        Returns:
            float: Median of the numeric values in the list.
        """
        # Sort the list
        sorted_lst = sorted(lst)
        
        # Calculate the median
        n = len(sorted_lst)
        if n % 2 == 1:
            median = sorted_lst[n // 2]
        else:
            median = (sorted_lst[n // 2 - 1] + sorted_lst[n // 2]) / 2
        
        return median

    def pricing_algorithm_creation(self,  role_name, function_id, function_name):
        """
        Creates a pricing algorithm based on role , converting project salaries and durations 
        into hourly rates in USD.
        Args:
            data (dict): A dictionary containing role information with the following keys:
                - role_id (int): The ID of the role.
                - role_name (str): The name of the role.
        Returns:
            dict: A dictionary with the calculated minimum and maximum hourly rates, project duration, 
                and currency. The keys are:
                - "min_salary" (float): The minimum hourly rate in USD, rounded to 3 decimal places.
                - "max_salary" (float): The maximum hourly rate in USD, rounded to 3 decimal places.
                - "duration" (int): The project duration, set to 1.
                - "currency" (str): The currency, set to a default value.
        """
        log_data = [f"info|| {datetime.now()}: Exception occured  while calculating pricing algorithm"]
        try:
            min_salary_overall_pricing = []
            max_slaver_overall_pricing = []
            project_duration_hours = []
            list_of_projects = Project.objects.filter( role__tag_name = role_name , function__id = function_id)
            # Princing filteration data based on projects and role or function
            pricing_values = Pricing.objects.filter(project__in = list_of_projects, 
                                                    stage = 3, active = True).values(
            "min_salary", "max_salary", "project_duration_unit", "project_duration", 
            "currency", "created", "modified"
            )
            pricing_values = list(self.arrange_date_format(pricing_values, function_name, role_name))
            
            # Iterating over pricing values and converting them into USD currency same for date format
            for val in pricing_values:
                try:
                    currency = val['currency']
                    min_salary = self.currency_conversion(val['min_salary'], currency)
                    max_salary = self.currency_conversion(val['max_salary'], currency)
                    
                    min_salary_overall_pricing.append(round(min_salary))
                    max_slaver_overall_pricing.append((max_salary))

                    project_duration_unit =  val['project_duration_unit']
                    project_duration = int(val['project_duration'])

                    project_duration_in_hour =self.conversion_of_day_in_hour(project_duration_unit, project_duration)
                    if project_duration_in_hour[1]:
                        project_duration_hours.append(project_duration_in_hour[0])
                except Exception as x:
                    log_data.append(f"error|| {str(x)}")
                    api_logging(log_data)
            # Adding extra flexibees interest rate
            min_salary_median = self.median_of_list(min_salary_overall_pricing)  + DEFAULT_ADDITIONAL_AMOUNT
            max_salary_median = self.median_of_list(max_slaver_overall_pricing)  + DEFAULT_ADDITIONAL_AMOUNT
            project_duration_median = self.median_of_list(project_duration_hours)

            # Calculating hourly rates
            min_hourly_rate = min_salary_median / project_duration_median
            max_hourly_rate = max_salary_median / project_duration_median

            return {
                "status" : "success",
                "errors" : "",
                "min_salary" : round(min_hourly_rate, 3),
                "max_salary" : round(max_hourly_rate, 3),
                "duration" : 1,
                "currency" : DEFAULT_CURRENCY
            }
        except Exception  as x :
            log_data.append(f"error|| {str(x)}")
            api_logging(log_data)
            return {
                "status" : "failure",
                "errors" : str(x),
                "min_salary" : 0,
                "max_salary" : 0,
                "duration" : 1,
                "currency" : DEFAULT_CURRENCY
            }

    def creating_models(self):
        try:
            response = []
            log_data = [f"info|| {datetime.now()}: Exception occured  while creating a data pricing roles"]
            # For Existing Roles Update and create data
            existing_roles_list = RoleMapping.objects.filter(is_active=True).distinct("role__id").values("role__id", "role__tag_name", "function__id", "function__tag_name")
            data =0 
            for role in existing_roles_list:
                role_id = role["role__id"]
                role_name = role["role__tag_name"]
                function_id = role["function__id"]
                function_name = role["function__tag_name"]
                try:
                    data = self.pricing_algorithm_creation(  role_name, function_id, function_name)
                    if data["status"] == "success":
                        role =  Role.objects.get(pk=role_id )
                        update_data = {
                            'min_salary': data["min_salary"],
                            'max_salary': data["max_salary"],
                            'currency': DEFAULT_CURRENCY
                        }

                        RolesMinMaxPricing.objects.update_or_create(existing_role=role, defaults=update_data)
                        response.append(data)
                except Exception as x:
                    log_data.append(f"error|| {str(x)}")
                    api_logging(log_data)

            # For Custome Roles Update and create data
            custom_role_list = CustomRole.objects.filter(is_active=True, status= PENDING_STATUS).values("id", "role_name", "function__id", "function__tag_name")

            for c_role in custom_role_list:

                role_id = c_role["id"]
                role_name = c_role["role_name"]
                function_id = c_role["function__id"]
                function_name = c_role["function__tag_name"]
                try :
                    data = self.pricing_algorithm_creation(  role_name, function_id, function_name)
                    if data["status"] == "success":
                        role =  CustomRole.objects.get(pk=role_id )
                        update_data = {
                            'min_salary': data["min_salary"],
                            'max_salary': data["max_salary"],
                            'currency': DEFAULT_CURRENCY
                        }
                        RolesMinMaxPricing.objects.update_or_create(custom_role=role, defaults=update_data)
                        response.append(data)
                except Exception as x:
                    log_data.append(f"error|| {str(x)}")
                    api_logging(log_data)
            
        except Exception as x:
            log_data.append(f"error|| {str(x)}")
            api_logging(log_data)
        

def  cron_job():
    try:
        log_data = [f"info|| {datetime.now()}: Pricing Algorithm "]
        chat_gpt = CandidatePricingAlgorithm()
        chat_gpt.creating_models()
    except Exception as x:
        log_data.append(f"error|| {str(x)}")
        api_logging(log_data)
