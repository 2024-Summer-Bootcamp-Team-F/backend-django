# __init__.py

from __future__ import absolute_import, unicode_literals

# 이 파일에서 Celery 애플리케이션을 임포트하여 Django가 항상 로드되도록 합니다.
from .celery import app as celery_app

__all__ = ('celery_app',)
