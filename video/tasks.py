import logging
import boto3
import requests
from celery import shared_task
from botocore.exceptions import NoCredentialsError
from .models import Video
import io
import time
import openai
import re
import environ

# 환경 변수 로드
env = environ.Env()
environ.Env.read_env()

# 로깅 설정
logger = logging.getLogger(__name__)

# OpenAI API 키 설정
openai.api_key = env("OPENAI_API_KEY")

def is_korean(text):
    # 간단하게 한국어 문자가 포함되어 있는지 확인
    return bool(re.search('[\u3131-\u3163\uac00-\ud7a3]', text))

def translate_text(text, source_language='ko', target_language='en'):
    try:
        headers = {
            'Authorization': f'Bearer {openai.api_key}',  # OpenAI API 키를 헤더에 포함
            'Content-Type': 'application/json'
        }
        data = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": f"Translate the following text from {source_language} to {target_language}."},
                {"role": "user", "content": text}
            ],
            "max_tokens": 100  # 최대 토큰 수를 100으로 설정
        }

        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()
        translation = response_json['choices'][0]['message']['content'].strip().strip('\"')
        return translation
    except Exception as e:
        logger.error("Error translating text: %s", e)
        return text

@shared_task
def generate_video_task(video_id, image_url, unique_filename, text_prompt):
    try:
        # 텍스트가 한국어인지 확인 후 번역
        if is_korean(text_prompt):
            translated_prompt = translate_text(text_prompt)
        else:
            translated_prompt = text_prompt

        video = Video.objects.get(id=video_id)
        api_key = env("VIDEO_API_KEY")
        url = "https://api.aivideoapi.com/runway/generate/imageDescription"

        payload = {
            "text_prompt": translated_prompt,
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
            uuid = response.json().get('uuid')
            if uuid:
                status_url = f"https://api.aivideoapi.com/status?uuid={uuid}"
                headers = {
                    "accept": "application/json",
                    "Authorization": f"Bearer {api_key}"
                }

                timeout = 30 * 60  # 30 minutes in seconds

                elapsed_time = 0
                polling_interval = 15  # seconds

                while True:
                    time.sleep(polling_interval)
                    elapsed_time += polling_interval

                    if elapsed_time > timeout:
                        logger.error("Polling timeout exceeded 30 minutes")
                        return

                    status_response = requests.get(status_url, headers=headers).json()
                    if status_response['status'] == 'success':
                        video_url = status_response['url']
                        break
                    elif status_response['status'] == 'failed':
                        logger.error("Video generation failed")
                        return

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
                logger.error("No UUID returned by API")
        else:
            logger.error(f"API request failed: {response.status_code}, {response.content}")
    except Exception as e:
        logger.error("Error in generate_video_task: %s", e)


def upload_to_s3(file_content, file_name, content_type):
    s3 = boto3.client('s3',
                      aws_access_key_id=env("AWS_ACCESS_KEY_ID"),
                      aws_secret_access_key=env("AWS_SECRET_ACCESS_KEY"),
                      region_name=env("AWS_S3_REGION_NAME"))

    try:
        s3.upload_fileobj(io.BytesIO(file_content), env("AWS_STORAGE_BUCKET_NAME_VIDEO"), file_name,
                          ExtraArgs={'ContentType': content_type})
        s3_url = f"https://{env('AWS_STORAGE_BUCKET_NAME_VIDEO')}.s3.{env('AWS_S3_REGION_NAME')}.amazonaws.com/{file_name}"
        return s3_url
    except NoCredentialsError:
        logger.error("Credentials not available")
        return None
    except Exception as e:
        logger.error("Error uploading to S3: %s", e)
        return None