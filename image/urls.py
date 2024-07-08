from django.urls import path
from .views import upload_image

urlpatterns = [
    path('api/v1/images/', upload_image, name='upload-image'),
]
