from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from django.conf import settings

# Django의 세팅 모듈을 Celery의 기본값으로 설정합니다.
# 커맨드라인에서 셀러리를 편하게 사용하기 위해 DJANGO_SETTINGS_MODULE
# 환경 변수를 기본 값으로 설정했습니다.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# 인스턴스를 만듭니다. 인스턴스를 여러 개 만들 수 있지만
# 장고를 사용하는 경우에는 굳이 그럴 필요없이 하나로 충분합니다.
app = Celery('backend')

# 여기서 문자열을 사용하는 것은 워커(worker)가
# 자식 프로세스로 설정 객체를 직렬화(serialize)하지 않아도 된다는 뜻입니다.
# 뒤에 namespace='CELERY'는 모든 셀러리 관련 설정 키는
# 'CELERY_' 라는 접두어를 가져야 한다고 알려줍니다.

# 여기에 문자열을 사용하면 작업자(worker)가 문자열로 이름을 추측할 수 있습니다.
# namespace='CELERY'는 모든 Celery 관련 설정 키가 'CELERY_' 접두사로 시작해야 함을 의미합니다.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Django의 모든 등록된 앱 구성에서 task 모듈을 불러옵니다.
# 보통 많은 경우에 재사용 가능한 app을 만들기 위해서는
# 모든 task를 별도의 분리된 tasks.py 모듈에 정의하는 것이 좋습니다.
# Celery는 아래 구문을 통해 task를 자동으로 탐색합니다.
# 각 앱마다 tasks.py 를 탐색합니다.
#개별 모듈을 일일이 CELERY_IMPORTS에 추가할 필요 없이 자동으로 인식합니다.
app.autodiscover_tasks()

# Q : 무조건 비동기 처리 할 작업을 task.py로 따로 빼야 하는거야?
#Celery를 사용하여 비동기 작업을 처리할 때, 작업을 tasks.py 파일로 분리하는 것은 좋은 관례이지만 필수는 아닙니다.
#이렇게 하면 코드가 더 깔끔하고 유지보수하기 쉬워집니다. 하지만 반드시 따로 파일로 분리해야 하는 것은 아니며
# 필요에 따라 동일한 파일에 작업을 정의할 수도 있습니다. : 노션에서 확인

#이유와 장점
#코드 구조: 비동기 작업을 별도의 파일에 정의하면, 동기 및 비동기 작업이 혼합되지 않아서 코드 구조가 더 명확해집니다.
#유지보수: 비동기 작업을 수정하거나 디버그할 때, 관련 코드가 한 곳에 모여 있어 유지보수가 더 쉬워집니다.
#테스트 용이성: 비동기 작업을 독립적으로 테스트할 수 있습니다.

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
