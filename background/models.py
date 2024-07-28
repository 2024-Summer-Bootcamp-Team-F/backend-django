from django.db import models
from image.models import Image
from user.models import User
class Background(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ForeignKey(Image, on_delete=models.CASCADE)
    gen_type = models.CharField(max_length=10, default='default_type')  # 기본값 설정
    concept_option = models.TextField(default='default_concept')  # 기본값 설정
    output_h = models.IntegerField()
    output_w = models.IntegerField()
    image_url = models.CharField(max_length=500, null=True, blank=True)  # null 값을 허용
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    recreated = models.BooleanField(default=False)

    def __str__(self):
        return f'Background {self.id} for {self.user.nickname}'


