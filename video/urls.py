from django.urls import path
from .views import videos_create, video_manage

urlpatterns = [
    path('videos/', videos_create, name='videos-create'),
    path('videos/<int:videoId>/', video_manage, name='video-manage'),
]
