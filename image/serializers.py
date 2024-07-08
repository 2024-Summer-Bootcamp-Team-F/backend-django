import uuid
from rest_framework import serializers
from .models import Image
import boto3
from django.conf import settings

import logging

logger = logging.getLogger(__name__)

#파일 업로드를 위한 필드
class ImageSerializer(serializers.ModelSerializer):
    file = serializers.ImageField(write_only=True)

    class Meta:
        model = Image
        fields = ['id', 'user', 'created_at', 'updated_at', 'is_deleted', 'image_url', 'file']
        #이미지url은 읽기 전용으로 생성
        read_only_fields = ('image_url',)

    def validate_file(self, value):
        """
        파일의 유효성을 검사합니다.
        """
        logger.debug("Uploaded file: ", value.name)

        # 여기서 파일의 유효성 검사 : 파일 크기나 형식 등..
        if not value.name.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
            raise serializers.ValidationError('유효하지 않은 파일 형식입니다. PNG, JPG, JPEG 또는 GIF 파일을 업로드하세요.')

        return value

    def create(self, validated_data):
        # 파일 데이터를 가져옴
        file = validated_data.pop('file')
        s3 = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME)

        # 파일명에 UUID를 추가하여 고유한 파일명 생성, 파일명 중복의 경우 s3에서 자동으로 덮어씌우기가 됨. 1 2 3 숫자를 붙이려 했지만 GPT 피셜 UUID를 사용하는게 더 좋다
        unique_filename = f"{uuid.uuid4()}_{file.name}"

        # S3에 파일 업로드

        s3.upload_fileobj(
            file,
            settings.AWS_STORAGE_BUCKET_NAME,
            unique_filename,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )

        #db에 저장 될 파일 url 생성
        file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{unique_filename}"
        # 이미지 URL을 데이터에 추가
        validated_data['image_url'] = file_url
        return super().create(validated_data)
