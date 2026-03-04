import os
from pathlib import Path

import environ
from django.utils.translation import gettext_lazy as _

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
)
env_file = BASE_DIR / '.env'
if env_file.exists():
    environ.Env.read_env(env_file)

SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

# ---------- Apps ----------
INSTALLED_APPS = [
    # modeltranslation must be before django.contrib.admin and project apps
    'modeltranslation',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'django_celery_beat',
    # Project apps
    'apps.core',
    'apps.tenants',
    'apps.positions',
    'apps.candidates',
    'apps.interviews',
    'apps.casestudies',
    'apps.evaluations',
    'apps.portal',
    'apps.chatbot',
    'apps.notifications',
]

# ---------- Middleware ----------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.core.middleware.TenantMiddleware',
    'apps.core.middleware.UserLanguageMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'apps.notifications.context_processors.unread_notification_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ---------- Database ----------
DATABASES = {
    'default': env.db('DATABASE_URL'),
}

# ---------- Auth ----------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/login/'

# ---------- i18n ----------
LANGUAGE_CODE = 'es'
LANGUAGES = [
    ('es', _('Español')),
    ('en', _('English')),
    ('ca', _('Català')),
]
LOCALE_PATHS = [BASE_DIR / 'locale']
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_TZ = True

# ---------- django-modeltranslation ----------
MODELTRANSLATION_DEFAULT_LANGUAGE = 'es'
MODELTRANSLATION_LANGUAGES = ('es', 'en', 'ca')
MODELTRANSLATION_FALLBACK_LANGUAGES = {'default': ('es',)}

# ---------- Static & Media ----------
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / env('MEDIA_ROOT', default='media/')
MEDIA_UPLOAD_TOKEN = env('MEDIA_UPLOAD_TOKEN', default='')

if env('AWS_STORAGE_BUCKET_NAME', default=''):
    # S3-compatible storage for media (Railway, production)
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='auto')
    AWS_S3_ENDPOINT_URL = env('AWS_S3_ENDPOINT_URL', default='')
    AWS_S3_CUSTOM_DOMAIN = env('AWS_S3_CUSTOM_DOMAIN', default='')
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default='')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default='')
    AWS_S3_FILE_OVERWRITE = False
    AWS_QUERYSTRING_AUTH = False
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/' if AWS_S3_CUSTOM_DOMAIN else f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/'
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
else:
    MEDIA_URL = '/media/'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# ---------- Email ----------
if env('EMAIL_HOST', default=''):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = env('EMAIL_HOST')
    EMAIL_PORT = env.int('EMAIL_PORT', default=587)
    EMAIL_HOST_USER = env('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
    EMAIL_USE_TLS = True
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@pekata.com')

# ---------- Celery ----------
CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# ---------- Anthropic AI ----------
ANTHROPIC_API_KEY = env('ANTHROPIC_API_KEY', default='')

# ---------- Google Calendar ----------
GOOGLE_CLIENT_ID = env('GOOGLE_CLIENT_ID', default='')
GOOGLE_CLIENT_SECRET = env('GOOGLE_CLIENT_SECRET', default='')
GOOGLE_REDIRECT_URI = env('GOOGLE_REDIRECT_URI', default='')

# ---------- Misc ----------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Max upload size: 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024
