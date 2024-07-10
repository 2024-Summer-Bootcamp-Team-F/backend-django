from celery import shared_task
import boto3
import uuid
import base64
from django.conf import settings
import logging
from io import BytesIO
from .models import Image

logger = logging.getLogger(__name__)


@shared_task
def upload_image_to_s3(file_name, file_content, content_type, image_id):
    logger.info(f"Started uploading {file_name} to S3")
    s3 = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME)
    unique_filename = f"{uuid.uuid4()}_{file_name}"
    file_content = base64.b64decode(file_content)  # base64로 인코딩된 파일 내용을 디코딩
    file_obj = BytesIO(file_content)  # 파일 내용을 BytesIO 객체로 변환

    # S3에 파일 업로드
    s3.upload_fileobj(
        file_obj,
        settings.AWS_STORAGE_BUCKET_NAME,
        unique_filename,
        ExtraArgs={
            "ContentType": content_type
        }
    )

    # 업로드된 파일의 URL 생성
    file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{unique_filename}"
    logger.info(f"Finished uploading {file_name} to S3, URL: {file_url}")

    # 데이터베이스 업데이트
    try:
        image_instance = Image.objects.get(id=image_id)
        image_instance.image_url = file_url
        image_instance.save()
        logger.info(f"Updated Image {image_id} with URL: {file_url}")
    except Image.DoesNotExist:
        logger.error(f"Image with id {image_id} does not exist")

    return file_url
