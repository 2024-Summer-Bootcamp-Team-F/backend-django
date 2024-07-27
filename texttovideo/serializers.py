from rest_framework import serializers
from .models import TextToVideo

class TextToVideoSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)  # user_id 필드를 추가 (쓰기 전용)
    video_url = serializers.CharField(read_only=True)  # video_url 필드를 읽기 전용으로 설정

    class Meta:
        model = TextToVideo
        fields = ['id', 'prompt', 'video_url', 'user_id']  # 필요한 모든 필드를 명시
