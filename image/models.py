from django.db import models
from user.models import User

class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    image_url = models.URLField(max_length=500, blank=True, null=True)  # 외부 URL을 위한 필드

    def __str__(self):
        return f"Image {self.id} by User {self.user.nickname}"
