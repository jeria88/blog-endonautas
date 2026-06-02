from .base import *
import dj_database_url

DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = [
    'endonautas.cl',
    'www.endonautas.cl',
    'app.endonautas.cl',
    '.railway.app',
]

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600)
}

CSRF_TRUSTED_ORIGINS = [
    'https://endonautas.cl',
    'https://www.endonautas.cl',
    'https://app.endonautas.cl',
    'https://*.railway.app',
]

SECURE_SSL_REDIRECT = False  # Cloudflare handles SSL
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

BREVO_API_KEY = os.environ.get('BREVO_API_KEY', '')
BREVO_DEFAULT_LIST_ID = int(os.environ.get('BREVO_DEFAULT_LIST_ID', '3'))

# Email real via Brevo SMTP
EMAIL_HOST = 'smtp-relay.brevo.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = True

POST_OFFICE = {
    'BACKENDS': {
        'default': 'django.core.mail.backends.smtp.EmailBackend',
    },
    'DEFAULT_PRIORITY': 'medium',
    'BATCH_SIZE': 20,
    'LOG_LEVEL': 1,
    'CELERY_ENABLED': False,  # Sin worker Celery — Railway Cron Job ejecuta send_queued_mail
    'DEFAULT_FROM_EMAIL': 'hola@endonautas.cl',
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}
