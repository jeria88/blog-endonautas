from .base import *
import dj_database_url

DEBUG = True  # TEMP: diagnosis 500 login — revertir después

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = [
    'endonautas.cl',
    'www.endonautas.cl',
    'app.endonautas.cl',
    '.railway.app',
]

DATABASES = {
    'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
}

CSRF_TRUSTED_ORIGINS = [
    'https://endonautas.cl',
    'https://www.endonautas.cl',
    'https://app.endonautas.cl',
]

SECURE_SSL_REDIRECT = False  # Cloudflare handles SSL
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
