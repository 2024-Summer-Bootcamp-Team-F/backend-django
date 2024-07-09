from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Django의 세팅 모듈을 Celery의 기본값으로 설정합니다.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

app = Celery('backend')

# 여기에 문자열을 사용하면 작업자(worker)가 문자열로 이름을 추측할 수 있습니다.
# namespace='CELERY'는 모든 Celery 관련 설정 키가 'CELERY_' 접두사로 시작해야 함을 의미합니다.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django의 모든 등록된 앱 구성에서 task 모듈을 불러옵니다.
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
