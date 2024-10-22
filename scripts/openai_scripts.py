import requests
from flexibees_candidate.settings import (AMAZON_AWS_ACCESS_ID_KEY, AMAZON_AWS_SECRET_ACCESS_KEY, AMAZON_AWS_REGION, AMAZON_AWS_MODEL_ID, AMAZON_SERVICE_NAME)
from apps.admin_app.views import api_logging
from datetime import datetime
from apps.employer.constants import ( YEARS, DURATION, CURRENCY_FORMAT)
import json
import boto3
from botocore.exceptions import ClientError

class AIServiceWrapperIntegration:
    """
    A class to interact with the OpenAI API via AWS for generating job descriptions and
    fetching hypothetical salary data.

    Attributes:
        aws_access_key_id (str): AWS access key ID for authentication.
        aws_secret_access_key (str): AWS secret access key for authentication.
        aws_region (str): AWS region where the service is hosted.
        model_id (str): The model ID for Amazon Bedrock, e.g., 'Titan Text Premier'.
        service_name (str): The AWS service name, e.g., 'bedrock-runtime'.

    Methods:
        execution_script(user_message):
            Sends a user message to the specified model and retrieves the response.

        generate_job_description_prompt(function_name, role, must_have_skills, experience, job_duration, number_of_hour_in_day):
            Generates a job description prompt based on the provided details.

        job_description_generate(function_name, role_name, skill_must_have, experience, job_duration, number_of_hour_in_day):
            Calls the OpenAI API to generate a job description based on the provided details.

        pricing_response_formatter(response):
            Formats the response from the OpenAI API into a list of dictionaries containing
            hypothetical salary data.

        pricing_data_fetched(function_name, role_name):
            Fetches hypothetical salary data for a specified function and role using the OpenAI API.
    """
    aws_access_key_id = AMAZON_AWS_ACCESS_ID_KEY
    aws_secret_access_key = AMAZON_AWS_SECRET_ACCESS_KEY
    aws_region = AMAZON_AWS_REGION  # Choose your desired region
    model_id = AMAZON_AWS_MODEL_ID
    service_name = AMAZON_SERVICE_NAME
    
    def execution_script( self, user_message ):
        
        """
        Sends a user message to the specified model and retrieves the response.

        Args:
            user_message (str): The user's message to be processed by the model.

        Returns:
            str: The text response from the model, or an empty string if an error occurs.
        """
        conversation = [
            {
                "role": "user",
                "content": [{"text": user_message}],
            }
        ]
        response_text = ""
        try:
            client = boto3.client(
            service_name = self.service_name ,
            region_name= self.aws_region,
            aws_access_key_id= self.aws_access_key_id,
            aws_secret_access_key= self.aws_secret_access_key
            )
            # Send the message to the model, using a basic inference configuration.
            response = client.converse(
                modelId = self.model_id,

                messages = conversation,
                inferenceConfig = {"maxTokens":2000,"temperature":0},
                additionalModelRequestFields = {"top_k":250}
            )

            # Extract and print the response text.
            response_text = response["output"]["message"]["content"][0]["text"]

            return response_text

        except (ClientError, Exception) as e:
            error = (f"ERROR: Can't invoke '{self.model_id}'. Reason: {e}")
            api_logging(error)
            return response_text
    
    # Prompt design for job description. 
    def generate_job_description_prompt(self,function_name, role, must_have_skills, experience, job_duration, number_of_hour_in_day):
        """
        Generates a job description prompt using the provided details.

        Args:
            function_name (str): The name of the function or department.
            role (str): The job role or title.
            must_have_skills (list): A list of must-have skills.
            experience (str): The required experience for the role.
            job_duration (str): The duration of the job.
            number_of_hour_in_day (str): Number of working hours in a day.

        Returns:
            str: The formatted job description prompt.
        """

        # Formulate the job description prompt based on the provided details
        prompt = f"""Create a job description: Function name: {function_name}, Role: {role}, Skills: {must_have_skills}. 
        Format (dont chnage the format): Job Description, Overview of the job, 
        Role & Responsibilities (4 points) 
        * .....                    
        * .....
        This is an Individual Contributor role, 
        
        Key Skills: {', '.join(must_have_skills)},
        job_duration : {job_duration}"""

        # Include number of hours in a day if provided
        if number_of_hour_in_day :
            prompt += f"\n Number of hours in a day: {number_of_hour_in_day}"

        # Include required experience if provided
        if experience :
            prompt += f"\n Experience required: {experience}"
        return prompt
    
    def job_description_generate(self,function_name="", role_name="", skill_must_have=[], experience=None, job_duration="", number_of_hour_in_day=""):
        """
        Calls the OpenAI API to generate a job description based on the provided details.

        Args:
            function_name (str): The name of the function or department.
            role_name (str): The job role or title.
            skill_must_have (list): A list of must-have skills.
            experience (str): The required experience for the role.
            job_duration (str): The duration of the job.
            number_of_hour_in_day (str): Number of working hours in a day.

        Returns:
            dict: The API response containing the generated job description.
        """
        res = ""
        
        try:
            # Generate the prompt for the job description
            prompt = self.generate_job_description_prompt(
                function_name = function_name, role = role_name, must_have_skills = skill_must_have, 
                 experience = experience, job_duration = job_duration, number_of_hour_in_day = number_of_hour_in_day
            )
            res = self.execution_script(prompt)
            return res
           
        except Exception as x:
            # Log the exception if something goes wrong
            log_data = [f"info|| {datetime.now()}: Exception occured in all candidates signUp report script"]
            log_data.append(f"error|| {x}")
            api_logging(log_data)
            res = x
            return res
    
    # Designing open ai for Pricing algorithm .

    def pricing_response_formatter(self,response):
        """
        Formats the response from the OpenAI API into a list of dictionaries containing
        hypothetical salary data.

        Args:
            response (dict): The JSON response from the OpenAI API containing salary data.

        Returns:
            list: A list of dictionaries containing formatted salary data with keys:
                - min_salary (float): Minimum salary in INR.
                - max_salary (float): Maximum salary in INR.
                - project_duration_unit (str): Unit of project duration (default: "years").
                - project_duration (str): Duration of the project (default: "1").
                - currency (str): Currency of the salary (default: "INR").
        """
        # Parse and format the salary data from the response
        result =[]
        try:
            data = json.loads(response)
        except Exception as e:
            log_data = [f"info|| {datetime.now()}: Formatting issue for pricing "]
            log_data.append(f"error|| {e}")
            data = response.split("JSON format:\n\n")[1]
            data= data.split("\n\nNote")[0]
            data = json.loads(data)
        response = data
        result = [
            {
                "min_salary":float(val['min_salary'].replace(",","")),
                "max_salary":float(val['max_salary'].replace(",","")),
                "project_duration_unit":YEARS,
                "project_duration":DURATION,
                "currency": CURRENCY_FORMAT
            } for val in response
        ]
        return result    
    
    def pricing_data_fetched(self, function_name , role_name):
        """
        Fetches hypothetical salary data for a specified function and role using the OpenAI API.

        Args:
            function_name (str): The function or job title for which salary data is requested.
            role_name (str): The role or position within the function for which salary data is requested.

        Returns:
            tuple: A tuple containing (success status, HTTP status code, formatted salary data)
                - success status (bool): True if the request was successful, False otherwise.
                - HTTP status code (int): The HTTP status code of the response.
                - formatted salary data (list): A list of dictionaries containing formatted salary data.
        """
        try:
            # Generate the prompt for fetching salary data
            prompt =  """
                        Generate a list of last year's hypothetical salary data points minimum  10 points for the ` """ + str(role_name) + """ ` role and ' """ + str(function_name) + """' function in the industry in India per year. Assume company sizes vary between 1 to 100, 1 to 500, and 1 to 1000 employees. Format the salaries in INR and output the data only in the following JSON format:  
                        [
                          {"min_salary": "", "max_salary": "" },
                          {"min_salary": "", "max_salary": "" },
                          ...
                        ]
            """
            # Calling execution script for fe
            response = self.execution_script(prompt)    
            data = self.pricing_response_formatter(response)
            return True , data
        except Exception as x:
            return False, x

        
