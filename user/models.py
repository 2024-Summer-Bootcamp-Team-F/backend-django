from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True)
    nickname = models.CharField(max_length=10, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True) # 최초 저장 시에만 현재 날짜
    updated_at = models.DateTimeField(auto_now=True) # 수정이 될 때마다 현재 날짜
    is_deleted = models.BooleanField(default=False)
