# background/tasks.py
from celery import shared_task
from .models import Background, Image, User
import requests
import io
import base64
import boto3
from PIL import Image as PILImage
import json
from django.conf import settings
import logging
import redis

logger = logging.getLogger(__name__)

# Redis 클라이언트 설정
redis_client = redis.StrictRedis(host='redis', port=6379, db=0)

@shared_task
def generate_background_task(background_id, user_id, image_id, gen_type, output_w, output_h, concept_option,
                             unique_filename):
    try:
        user = User.objects.get(id=user_id)
        image = Image.objects.get(id=image_id)
        image_url = image.image_url
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        image_file = io.BytesIO(image_response.content)

        url = "https://api.draph.art/v1/generate/"
        headers = {'Authorization': f'Bearer {settings.DRAPHART_API_KEY}'}
        files = {'image': ('image.jpg', image_file, 'image/jpeg')}
        data = {
            "username": settings.DRAPHART_USER_NAME,
            "gen_type": gen_type,
            "multiblob_sod": settings.DRAPHART_MULTIBLOD_SOD,
            "output_w": output_w,
            "output_h": output_h,
            "bg_color_hex_code": settings.DRAPHART_BD_COLOR_HEX_CODE,
            'concept_option': json.dumps(concept_option),
        }

        response = requests.post(url, headers=headers, data=data, files=files)
        response_data = response.content
        image_data = base64.b64decode(response_data)
        image_bytes = io.BytesIO(image_data)
        pil_image = PILImage.open(image_bytes)
        pil_image = pil_image.convert('RGB')
        png_image_bytes = io.BytesIO()
        pil_image.save(png_image_bytes, format='PNG')
        png_image_bytes.seek(0)

        s3 = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME)
        s3.upload_fileobj(png_image_bytes, settings.AWS_STORAGE_BUCKET_NAME, unique_filename,
                          ExtraArgs={'ContentType': 'image/png'})
        s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{unique_filename}"

        # Background 모델 업데이트
        background_instance = Background.objects.get(id=background_id)
        background_instance.image_url = s3_url
        background_instance.save()

        redis_client.delete(f'background_image_url_{image_id}')

        return {"background_id": background_instance.id, "image_url": s3_url}
    except Exception as e:
        logger.error("Error in generate_background_task: %s", e)
        return {"error": str(e)}
