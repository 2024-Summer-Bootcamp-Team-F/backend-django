# image/models.py

from django.db import models
from user.models import User

class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) #만약 오류뜨면 -> , default=1 설정 넣어줘서 입력. 처음에는 사용자가 없어서 오류남
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    image_url = models.URLField(max_length=500)

    def __str__(self):
        return f"Image {self.id} by User {self.user.nickname}"

