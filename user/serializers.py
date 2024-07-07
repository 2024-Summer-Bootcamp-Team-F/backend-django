from rest_framework import serializers

from user.models import User

import logging
logger = logging.getLogger(__name__)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class NicknameCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['nickname']

    def validate_nickname(self, value):
        """
        닉네임 중복 및 공백 검사
        """
        # 공백 제거 후 검사
        stripped_value = value.strip()
        logger.debug("stripped_value: ", stripped_value)

        if not stripped_value:
            raise serializers.ValidationError('닉네임을 입력하세요.')

        if User.objects.filter(nickname=value).exists():
            raise serializers.ValidationError('중복된 닉네임입니다.')

