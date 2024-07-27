from django.db import models
from user.models import User
from background.models import Background

class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    background = models.ForeignKey(Background, on_delete=models.CASCADE)
    video_url = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'Video {self.id} for {self.user.username}'
