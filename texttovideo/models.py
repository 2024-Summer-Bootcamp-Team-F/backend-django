from django.db import models
from user.models import User

class TextToVideo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)  # 기본 값을 1로 설정하여 초기 사용자 없음에 따른 오류 방지
    prompt = models.CharField(max_length=255)
    video_url = models.CharField(max_length=2048)  # 최대 길이를 2048로 늘림
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"TextToVideo {self.id} by User {self.user.nickname}"
