from rest_framework import serializers
from .models import Image
from .tasks import upload_image_to_s3 #얘도 추가!
import logging

logger = logging.getLogger(__name__)

class ImageSerializer(serializers.ModelSerializer):
    file = serializers.ImageField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Image
        fields = ['id', 'user_id', 'created_at', 'updated_at', 'is_deleted', 'image_url', 'file']
        read_only_fields = ('image_url', 'created_at', 'updated_at', 'is_deleted')

    def validate_file(self, value):
        """
        파일의 유효성을 검사합니다.
        """
        logger.debug("Uploaded file: %s", value.name)
        if not value.name.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
            raise serializers.ValidationError('유효하지 않은 파일 형식입니다. PNG, JPG, JPEG 또는 GIF 파일을 업로드하세요.')
        return value

    def create(self, validated_data):
        user_id = validated_data.pop('user_id')
        validated_data['user_id'] = user_id


        validated_data.pop('file')  # file 필드를 제거하여 모델에 저장하지 않도록 합니다.


        return super().create(validated_data)