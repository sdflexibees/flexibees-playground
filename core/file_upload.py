import uuid
from apps.common.constants import EMPLOYER
import boto3
from flexibees_candidate.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME, AWS_S3_CUSTOM_DOMAIN, ENV
from core.constants import HTTPS

# bucket session
session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
s3 = session.resource('s3')

# file name conversion
def file_name_conversion(directory, file_extension):
    filename = '{}.{}'.format(uuid.uuid4().hex, file_extension)
    return '{0}/{1}'.format(directory, filename).lower()

# upload the file to s3 bucket
def upload_to_s3_bucket(file_to_upload, directory, file_extension):

    # Include the environment in the directory path
    full_directory = f'{EMPLOYER}/{ENV}/{directory}'
    
    cloud_filename = file_name_conversion(full_directory, file_extension)
    try:
        s3.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(
            Key=cloud_filename, Body=file_to_upload, ACL='public-read')
    except Exception:
        return None
    return f"{HTTPS}://{AWS_S3_CUSTOM_DOMAIN}/{cloud_filename}"

