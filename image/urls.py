from django.urls import path
from .views import upload_image, image_manage

urlpatterns = [
    path('api/v1/images/', upload_image, name='upload-image'),  # 이미지 업로드 엔드포인트
    path('api/v1/images/<int:image_id>/', image_manage, name='image-detail'),  # 이미지 조회 및 삭제 엔드포인트
]
