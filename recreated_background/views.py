from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import RecreatedBackground, Background
from .serializers import RecreatedBackgroundSerializer
import requests
import io
import uuid
import base64
import boto3
from PIL import Image as PILImage
import json
import logging
from django.conf import settings

# 로깅 설정
logger = logging.getLogger(__name__)

@swagger_auto_schema(method='post',
    operation_id='AI 배경 이미지 재생성',
    operation_description='AI 배경 이미지를 재생성합니다.',
    tags=['Recreated Background'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'concept_option': openapi.Schema(type=openapi.TYPE_OBJECT, description='Concept Option', properties={
                'category': openapi.Schema(type=openapi.TYPE_STRING, description='Category', enum=['cosmetics', 'food', 'clothes', 'person', 'car', 'others']),
                'theme': openapi.Schema(type=openapi.TYPE_STRING, description='Theme'),
                'num_results': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of Results', minimum=1, maximum=4)
            }),
        },
        required=['concept_option']
    ),
    responses={
        201: openapi.Response('Recreated Image Successfully', RecreatedBackgroundSerializer),
        400: 'Bad Request',
        404: 'Not Found',
        500: 'Internal Server Error'
    }
)
@api_view(['POST'])
def recreate_background_view(request):
    # 요청 데이터에서 필요한 값을 추출
    concept_option = request.data.get('concept_option')

    logger.debug("Received request data: %s", request.data)

    # 필수 값이 있는지 확인
    if not concept_option:
        logger.debug("Missing required parameter: concept_option")
        return Response({"error": "concept_option is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # 사용자의 가장 최근에 생성된 Background 객체를 가져옴
        background = Background.objects.latest('created_at')
        logger.debug("Fetched latest background: %s", background)
    except Background.DoesNotExist:
        return Response({"error": "Background not found"}, status=status.HTTP_404_NOT_FOUND)

    user = background.user
    image = background.image

    # 이미지 테이블에 있는 사용자가 업로드한 사진의 URL을 다운로드
    image_url = image.image_url
    try:
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        image_file = io.BytesIO(image_response.content)
        logger.debug("Downloaded image from URL: %s", image_url)
    except requests.RequestException as e:
        logger.error("Failed to download image: %s", e)
        return Response({"error": "Failed to download image"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # API 호출 준비
    url = "https://api.draph.art/v1/generate/"
    headers = {'Authorization': f'Bearer {settings.DRAPHART_API_KEY}'}

    # 파일 객체에 파일 이름을 수동으로 추가
    files = {
        'image': ('image.jpg', image_file, 'image/jpeg')
    }

    # 요청 데이터 구성
    data = {
        "username": settings.DRAPHART_USER_NAME,
        "gen_type": background.gen_type,
        "output_w": background.output_w,
        "output_h": background.output_h,
        'concept_option': json.dumps(concept_option),
    }

    # API 호출
    response = requests.post(url, headers=headers, data=data, files=files)

    if response.status_code != 200:
        logger.debug("AI 이미지 생성 실패: %s", response.text)
        return Response({"error": "AI 이미지 생성 실패", "details": response.text}, status=status.HTTP_400_BAD_REQUEST)

    response_data = response.content

    try:
        # base64 이미지를 디코딩하고 처리
        image_data = base64.b64decode(response_data)
        image_bytes = io.BytesIO(image_data)
        pil_image = PILImage.open(image_bytes)
        pil_image = pil_image.convert('RGB')
        png_image_bytes = io.BytesIO()
        pil_image.save(png_image_bytes, format='PNG')
        png_image_bytes.seek(0)

        # S3에 업로드
        s3 = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME)
        unique_filename = f"{uuid.uuid4()}.png"
        s3.upload_fileobj(png_image_bytes, settings.AWS_STORAGE_BUCKET_NAME, unique_filename, ExtraArgs={'ContentType': 'image/png'})
        s3_url = f"http://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{unique_filename}"

    except Exception as e:
        logger.error("Error uploading to S3: %s", e)
        return Response({"error": "Failed to upload image to S3", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # RecreatedBackground 모델에 저장
    recreated_background = RecreatedBackground.objects.create(
        background=background,
        concept_option=concept_option,
        image_url=s3_url,
    )

    # 성공적으로 저장되었음을 클라이언트에게 반환
    serializer = RecreatedBackgroundSerializer(recreated_background)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@swagger_auto_schema(
    method='get',
    operation_id='재생성된 이미지 조회',
    operation_description='재생성된 이미지를 조회합니다.',
    tags=['Recreated Background'],
    responses={
        200: RecreatedBackgroundSerializer,
        404: "Recreated Background not found.",
    }
)
@swagger_auto_schema(
    method='delete',
    operation_id='재생성된 이미지 삭제',
    operation_description='재생성된 이미지를 삭제합니다.',
    tags=['Recreated Background'],
    responses={
        200: openapi.Response("Image deleted successfully."),
        404: "Recreated Background not found.",
    }
)
@api_view(['GET', 'DELETE'])
def recreated_background_manage(request, recreated_backgroundId):
    try:
        # 재생성된 배경 이미지 객체를 가져옴
        recreated_background = RecreatedBackground.objects.get(id=recreated_backgroundId)
    except RecreatedBackground.DoesNotExist:
        return Response({"error": "해당 재생성된 배경 이미지가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        # 재생성된 배경 이미지를 직렬화하여 반환
        serializer = RecreatedBackgroundSerializer(recreated_background)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        s3 = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME)
        file_key = recreated_background.image_url.split('/')[-1]
        try:
            # S3에서 파일 삭제
            s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key)
        except Exception as e:
            logger.error("S3 파일 삭제 오류: %s", e)
            return Response({"error": "S3 파일 삭제 오류", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 재생성된 배경 이미지 객체 삭제
        recreated_background.delete()
        return Response({"message": "Image deleted successfully."}, status=status.HTTP_200_OK)
