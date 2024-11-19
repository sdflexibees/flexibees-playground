import uuid
import boto3

from flexibees_finance.settings import AWS_STORAGE_BUCKET_NAME, AWS_S3_CUSTOM_DOMAIN, AWS_ACCESS_KEY_ID, \
    AWS_SECRET_ACCESS_KEY

session = boto3.session.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
s3 = session.resource('s3')


def file_name_conversion(instance, filename, directory):
    ext = filename.split('.')[-1]
    filename = '{}.{}'.format(uuid.uuid4().hex, ext)
    return '{0}/{1}/{2}'.format(directory, instance, filename).lower()


def upload_file(instance, fileToUpload, directory='images'):

    cloud_filename = file_name_conversion(instance, fileToUpload.name, directory)

    try:
        s3.Bucket(AWS_STORAGE_BUCKET_NAME).put_object(Key=cloud_filename, Body=fileToUpload, ACL='public-read')
    except:
        print('error')
    return "https://{0}/{1}".format(AWS_S3_CUSTOM_DOMAIN, cloud_filename)
