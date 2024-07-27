from django.urls import path
from .views import create_video, handle_video

urlpatterns = [
    path('', create_video, name='create_video'),
    path('<int:videoId>/', handle_video, name='handle_video'),
]
