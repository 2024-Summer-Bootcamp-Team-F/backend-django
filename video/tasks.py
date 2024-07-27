import boto3
import requests
from celery import shared_task
from botocore.exceptions import NoCredentialsError
from django.conf import settings
from .models import Video
import logging
import io
import uuid

# 로깅 설정
logger = logging.getLogger(__name__)

@shared_task
def generate_video_task(video_id, image_url, unique_filename):
    try:
        video = Video.objects.get(id=video_id)
        api_key = settings.VIDEO_API_KEY
        url = "https://api.aivideoapi.com/runway/generate/image"

        payload = {
            "img_prompt": image_url,
            "motion": 5,
            "seed": 0,
            "upscale": True,
            "interpolate": True,
            "callback_url": ""  # 빈 문자열로 설정
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            video_url = response.json().get('video_url')
            if video_url:
                video_response = requests.get(video_url)
                video_response.raise_for_status()  # Raise an error on bad status
                video_content = video_response.content

                s3_url = upload_to_s3(video_content, unique_filename, 'video/mp4')

                if s3_url:
                    video.video_url = s3_url
                    video.save()
                else:
                    logger.error("S3 upload failed")
            else:
                logger.error("No video URL returned by API")
        else:
            logger.error(f"API request failed: {response.status_code}, {response.content}")
    except Exception as e:
        logger.error("Error in generate_video_task: %s", e)


def upload_to_s3(file_content, file_name, content_type):
    s3 = boto3.client('s3',
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                      region_name=settings.AWS_S3_REGION_NAME)

    try:
        s3.upload_fileobj(io.BytesIO(file_content), settings.AWS_STORAGE_BUCKET_NAME, file_name,
                          ExtraArgs={'ContentType': 'video/mp4'})
        s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{file_name}"
        return s3_url
    except NoCredentialsError:
        logger.error("Credentials not available")
        return None
    except Exception as e:
        logger.error("Error uploading to S3: %s", e)
        return None
