from django.db import models
from user.models import User
from image.models import Image

class BackgroundImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    gen_type = models.CharField(max_length=10)
    concept_option = models.CharField(max_length=500)  # 필드 길이 증가
    output_h = models.IntegerField()
    output_w = models.IntegerField()
    image_url = models.URLField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    recreated = models.BooleanField(default=False)

    def __str__(self):
        return f"BackgroundImage {self.id} for {self.user.nickname}"
