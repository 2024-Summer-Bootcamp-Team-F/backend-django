import uuid
from rest_framework import serializers
from .models import Image
import boto3
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class ImageSerializer(serializers.ModelSerializer):
    file = serializers.ImageField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Image
        fields = ['id', 'user_id', 'created_at', 'updated_at', 'is_deleted', 'image_url', 'file']
        read_only_fields = ('image_url', 'created_at', 'updated_at')

    def validate_file(self, value):
        """
        파일의 유효성을 검사합니다.
        """
        logger.debug("Uploaded file: ", value.name)
        if not value.name.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
            raise serializers.ValidationError('유효하지 않은 파일 형식입니다. PNG, JPG, JPEG 또는 GIF 파일을 업로드하세요.')
        return value

    def create(self, validated_data):
        # user_id 필드를 user 필드로 변환
        user_id = validated_data.pop('user_id')
        validated_data['user_id'] = user_id

        # 파일 데이터를 가져옴
        file = validated_data.pop('file')
        s3 = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME)
        unique_filename = f"{uuid.uuid4()}_{file.name}"
        s3.upload_fileobj(
            file,
            settings.AWS_STORAGE_BUCKET_NAME,
            unique_filename,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )
        file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{unique_filename}"
        validated_data['image_url'] = file_url

        return super().create(validated_data)
