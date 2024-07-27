from pathlib import Path
import os
import environ
import pymysql
import logging
from elasticsearch import Elasticsearch

# MySQLdb 대신 pymysql 사용
pymysql.install_as_MySQLdb()

# 현재 파일의 부모 디렉토리로 설정
BASE_DIR = Path(__file__).resolve().parent.parent  # 변경된 부분: 부모 디렉토리를 올바르게 설정

# .env 파일 경로 설정
env_file = os.path.join(BASE_DIR, 'backend', '.env')  # 변경된 부분: .env 파일 경로 지정

# 환경 변수를 설정
env = environ.Env()

# .env 파일을 UTF-8로 읽기
with open(env_file, 'r', encoding='utf-8') as f:
    env.read_env(f)

# Django의 SECRET_KEY 및 OpenAI API 키 설정
SECRET_KEY = env('SECRET_KEY')
OPENAI_API_KEY = env('OPENAI_API_KEY')

# 디버그 모드 활성화
DEBUG = True

ALLOWED_HOSTS = ['*']

# 애플리케이션 정의
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'drf_yasg',
    'user',
    'storages',
    'image',
    'background',
    'recreated_background',
    'banner',
    'django_redis',
    'image_resizing',
    'django_celery_results',
    'django_prometheus',
    'django_celery_beat',
    'corsheaders',
    'video',
]

# 미들웨어 설정
MIDDLEWARE = [
    'django_prometheus.middleware.PrometheusBeforeMiddleware',  # 모니터링 미들웨어 (시작)
    'corsheaders.middleware.CorsMiddleware',                    # CORS 설정
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',               # 정적 파일 처리 미들웨어
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_prometheus.middleware.PrometheusAfterMiddleware',   # 모니터링 미들웨어 (끝)
]

# URL 설정
ROOT_URLCONF = 'backend.urls'

# 템플릿 설정
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Swagger 설정
SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': {
        'Token': {
            'type': 'apiKey',
            'name': 'bootcamp',
            'in': 'header'
        }
    },
}

# WSGI 애플리케이션 경로
WSGI_APPLICATION = 'backend.wsgi.application'

# 데이터베이스 설정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': env('DATABASE_NAME'),
        'USER': env('DATABASE_USER'),
        'PASSWORD': env('DATABASE_PASS'),
        'HOST': env('DATABASE_HOST'),
        'PORT': '3306',
        'CONN_MAX_AGE': 0,  # 매 쿼리마다 새로운 커넥션을 생성
    }
}

# 비밀번호 검증기 설정
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

# 국제화 설정
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = True

# 정적 파일 설정
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Whitenoise 설정
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 기본 primary key 필드 타입 설정
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS 설정
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

# AWS S3 설정
AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME')
AWS_QUERYSTRING_AUTH = False

# 기본 파일 저장 설정 (S3 사용)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# DRF 설정
REST_FRAMEWORK = {
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ),
}

# OpenAI API 키 설정
OPENAI_API_KEY = env('OPENAI_API_KEY')

# 추가 환경 변수 설정
DRAPHART_API_KEY = env('DRAPHART_API_KEY')
DRAPHART_USER_NAME = env('DRAPHART_USER_NAME')
DRAPHART_MULTIBLOD_SOD = env('DRAPHART_MULTIBLOD_SOD')
DRAPHART_BD_COLOR_HEX_CODE = env('DRAPHART_BD_COLOR_HEX_CODE')

# Celery 설정
CELERY_BROKER_URL = 'amqp://guest:guest@rabbitmq:5672//'  # RabbitMQ 설정 (아이디:비밀번호)
CELERY_RESULT_BACKEND = 'django-db'  # 작업 결과를 Django 데이터베이스에 저장
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Seoul'
CELERY_CACHE_BACKEND = 'default'
CELERY_WORKER_HIJACK_ROOT_LOGGER = False  # Celery가 root logger를 hijack하지 않도록 설정

CELERYD_TASK_TIME_LIMIT = 300  # 작업 제한 시간 설정 (초)
CELERYD_TASK_SOFT_TIME_LIMIT = 270  # 소프트 제한 시간 설정 (초)

# Redis 설정 (Django 캐시)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',  # Redis 서버 위치
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# 커스텀 Elasticsearch 핸들러 정의
class ElasticsearchHandler(logging.Handler):
    def __init__(self, hosts=None, index='django-logs'):
        logging.Handler.__init__(self)
        self.es = Elasticsearch(hosts=hosts)
        self.index = index

    def emit(self, record):
        log_entry = self.format(record)
        self.es.index(index=self.index, document={'message': log_entry})

# LOGGING 설정
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'debug.log'),  # 로그 파일 경로
            'formatter': 'verbose',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 5,  # 백업 파일 수
        },
    },
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

VIDEO_API_KEY = env('VIDEO_API_KEY')
AWS_STORAGE_BUCKET_NAME_VIDEO = env('AWS_STORAGE_BUCKET_NAME_VIDEO')
