"""
Django settings for flexibees_candidate project.
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
file_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'wxe$p$u2=sg97wq=_8a3ub1e7x43sa4o@qf#e6uv7$g66z1z3j'
SECRET_CIPHER_KEY = b'PoP9ut4c5vC81Zx2UGdASQ3Lsr8hDqv8BO9FzIDr6HQ='


ALLOWED_HOSTS = ['*']


# Application definition
PREREQUISITE_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'drf_yasg',
    'storages',
    'channels',
    'django_crontab',
    'commands'
]


PROJECT_APPS = [
    'apps.admin_app',
    'apps.projects',
    'apps.notifications',
    'apps.candidate',
    'apps.availability',
    "apps.common",
    'apps.employer',
    'apps.finance'
]

INSTALLED_APPS = PREREQUISITE_APPS + PROJECT_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.response_format.ResponseFormatMiddleware',
    # 'django_cprofile_middleware.middleware.ProfilerMiddleware',
]

# DJANGO_CPROFILE_MIDDLEWARE_REQUIRE_STAFF = False

ROOT_URLCONF = 'flexibees_candidate.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries':{
                'load_constants': 'core.templatetags.load_constants',
            }
        },
    },
]

WSGI_APPLICATION = 'flexibees_candidate.wsgi.application'

ASGI_APPLICATION = 'flexibees_candidate.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('redis-prod-server', 6379)],
            # 'capacity': 300
        },
    },
}


# Password validation
# https://docs.djangoproject.com/en/3.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

CORS_ORIGIN_ALLOW_ALL = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.1/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "static_files")

SWAGGER_SETTINGS = {
   'SECURITY_DEFINITIONS': {
      '': {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
      }
   }
}

MAX_CHARS_ID = 100
MAX_CHARS_DEAL_NAME = 200
MAX_CHARS_ACCOUNT_NAME = 100
MAX_CHARS_CONTACT_NAME = 100
MAX_CHARS_ROLE_TYPE = 120
MAX_CHARS_MODEL_TYPE = 100
MAX_CHARS_FLEXI_DETAILS = 60
MAX_CHARS_STAGE = 30
FIRST_STAGE_STATUS = 1

RESUME_DOWNLOAD_PATH = "/resume/"
RESUME_ALLOWED_UPLOAD_EXTENSIONS = ['docx', 'pdf', 'doc']

# On-Behalf of Candidate Send notification to Admins from Super-Admin
SUPER_ADMIN_EMAIL = "rashmi@flexibees.com"
SUPER_ADMIN_ROLE = "{super_admin}"


# Validation related to Character Limit
CHARACTER_LIMIT_60 = 60
CHARACTER_LIMIT_120 = 120


# Notification Constants
SENT_TO_TYPE_SUPER_ADMIN = 'super_admin'
SENT_TO_TYPE_RECRUITER_ADMIN = 'admin'
SENT_TO_TYPE_RECRUITER = 'recruiter'
ITEM_TYPE_CANDIDATE = 'candidate'

# minimum hours to be filled in my typical day to move the candidate from functional to flexifit
MIN_HOURS_FOR_MY_TYPICAL_DAY = 15
HOURS_A_DAY = 24
MAX_NO_OF_MY_TYPICAL_DAY_NOTIFICATIONS = 5
AVAILABILITY_REAPPEAR_REMINDER_NOTIFICATION_COUNT = 4
NOTIFICATION_ICON = 'https://flexprod.s3.ap-south-1.amazonaws.com/flexibee_logo.png'
CLOSED_PROJECT_STATUS = 9
SUSPENDED_PROJECT_STATUS = 11

# max image size 
IMAGE_MAX_SIZE = '5242880' # 5mb
FCM_CREDENTIALS_PATH = 'files/fcm_credentials.json'
FCM_NOTIFICATION_URL = "https://fcm.googleapis.com/v1/projects/{project_id}/messages:send"
FCM_SCOPES = ['https://www.googleapis.com/auth/firebase.messaging']
