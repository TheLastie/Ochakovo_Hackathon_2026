import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parents[2]
DEBUG = os.getenv('OCHAKOVO_DEBUG', '1') == '1'
SECRET_KEY = os.getenv('SECRET_KEY', 'local-prototype-only-do-not-deploy')
if not DEBUG and SECRET_KEY == 'local-prototype-only-do-not-deploy':
 raise RuntimeError('Set SECRET_KEY before deployment')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '127.0.0.1,localhost,testserver').split(',')
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',') if origin.strip()]
# Enable only behind the documented trusted HTTPS proxy, which overwrites this header.
if os.getenv('TRUST_PROXY_HEADERS', '0') == '1':
 SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = os.getenv('SECURE_COOKIES', '0') == '1'
CSRF_COOKIE_SECURE = SESSION_COOKIE_SECURE
INSTALLED_APPS = ['django.contrib.admin','django.contrib.auth','django.contrib.contenttypes','django.contrib.sessions','django.contrib.messages','django.contrib.staticfiles','rest_framework','career']
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware','django.contrib.sessions.middleware.SessionMiddleware','django.middleware.common.CommonMiddleware','django.middleware.csrf.CsrfViewMiddleware','django.contrib.auth.middleware.AuthenticationMiddleware','django.contrib.messages.middleware.MessageMiddleware','django.middleware.clickjacking.XFrameOptionsMiddleware']
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{'BACKEND':'django.template.backends.django.DjangoTemplates','DIRS':[BASE_DIR/'web/templates'],'APP_DIRS':True,'OPTIONS':{'context_processors':['django.template.context_processors.request','django.contrib.auth.context_processors.auth','django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION = 'config.wsgi.application'
DATABASES = {'default': {'ENGINE':'django.db.backends.postgresql','NAME':os.getenv('POSTGRES_DB','ochakovo'),'USER':os.getenv('POSTGRES_USER','ochakovo'),'PASSWORD':os.getenv('POSTGRES_PASSWORD',''),'HOST':os.getenv('POSTGRES_HOST'),'PORT':os.getenv('POSTGRES_PORT','5432')}} if os.getenv('POSTGRES_HOST') else {'default':{'ENGINE':'django.db.backends.sqlite3','NAME':BASE_DIR/'local.sqlite3'}}
LANGUAGE_CODE='ru-ru'
TIME_ZONE='Asia/Yekaterinburg'
USE_TZ=True
STATIC_URL='/static/'
STATIC_ROOT=BASE_DIR/'staticfiles'
STATICFILES_DIRS=[('app',BASE_DIR/'web/dist'),('brand',BASE_DIR/'brand')]
DEFAULT_AUTO_FIELD='django.db.models.BigAutoField'
DATA_UPLOAD_MAX_MEMORY_SIZE=16384
SESSION_COOKIE_HTTPONLY=True
SECURE_CONTENT_TYPE_NOSNIFF=True
REST_FRAMEWORK={'DEFAULT_THROTTLE_CLASSES':['rest_framework.throttling.AnonRateThrottle'],'DEFAULT_THROTTLE_RATES':{'anon':'30/min'}}
