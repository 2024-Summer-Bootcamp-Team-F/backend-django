from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Background, Image, User
from .serializers import BackgroundSerializer
import requests
import io
import uuid
import base64
import boto3
from PIL import Image as PILImage
import json
import logging
from django.conf import settings
from .tasks import generate_background_task

# 로깅 설정
logger = logging.getLogger(__name__)

# 허용된 이미지 생성 유형
GEN_TYPES = ['remove_bg', 'color_bg', 'simple', 'concept']

# Swagger를 사용하여 API 문서화
@swagger_auto_schema(method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='User ID'),
            'image_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='Image ID'),
            'gen_type': openapi.Schema(type=openapi.TYPE_STRING, description='Generation Type', enum=['remove_bg', 'color_bg', 'simple', 'concept']),
            'output_w': openapi.Schema(type=openapi.TYPE_INTEGER, description='Output Width', default=1000, minimum=200, maximum=2000),
            'output_h': openapi.Schema(type=openapi.TYPE_INTEGER, description='Output Height', default=1000, minimum=200, maximum=2000),
            'concept_option': openapi.Schema(type=openapi.TYPE_OBJECT, description='Concept Option', properties={
                'category': openapi.Schema(type=openapi.TYPE_STRING, description='Category', enum=['cosmetics', 'food', 'clothes', 'person', 'car', 'others']),
                'theme': openapi.Schema(type=openapi.TYPE_STRING, description='Theme'),
                'num_results': openapi.Schema(type=openapi.TYPE_INTEGER, description='Number of Results', minimum=1, maximum=4)
            }),
        },
        required=['user_id', 'image_id', 'gen_type']
    ),
    responses={
        201: openapi.Response('AI 이미지 생성 성공', BackgroundSerializer(many=True)),
        400: 'Bad Request',
        500: 'Internal Server Error'
    }
)
@api_view(['POST'])
def backgrounds_view(request):
    user_id = request.data.get('user_id')
    image_id = request.data.get('image_id')
    gen_type = request.data.get('gen_type')
    output_h = request.data.get('output_h', 1000)
    output_w = request.data.get('output_w', 1000)
    concept_option = request.data.get('concept_option', {})

    if not (user_id and image_id and gen_type):
        return Response({"error": "user_id, image_id, and gen_type are required"}, status=status.HTTP_400_BAD_REQUEST)

    if gen_type not in GEN_TYPES:
        return Response({"error": f"gen_type is invalid. 가능한 값 : {', '.join(GEN_TYPES)}"},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "사용자 없음"}, status=status.HTTP_404_NOT_FOUND)

    try:
        image = Image.objects.get(id=image_id)
    except Image.DoesNotExist:
        return Response({"error": "이미지 없음"}, status=status.HTTP_404_NOT_FOUND)

    unique_filename = f"{uuid.uuid4()}.png"
    background_instance = Background.objects.create(
        user=user,
        image=image,
        gen_type=gen_type,
        concept_option=json.dumps(concept_option),
        output_w=output_w,
        output_h=output_h,
        image_url=None  # URL은 생성 후 업데이트
    )

    task = generate_background_task.delay(background_instance.id, user_id, image_id, gen_type, output_w, output_h, concept_option, unique_filename)

    return Response({
        "background_id": background_instance.id
    }, status=status.HTTP_202_ACCEPTED)

@swagger_auto_schema(
    method='get',
    operation_id='생성된 이미지 조회',
    operation_description='생성된 이미지를 조회합니다.',
    tags=['backgrounds'],
    responses={
        200: BackgroundSerializer,
        404: "Background not found.",
    }
)
@swagger_auto_schema(
    method='put',
    operation_id='생성된 이미지 수정',
    operation_description='생성된 이미지를 수정합니다.',
    tags=['backgrounds'],
    responses={
        200: BackgroundSerializer,
        400: "Bad Request",
        404: "Background not found.",
    }
)
@swagger_auto_schema(
    method='delete',
    operation_id='생성된 이미지 삭제',
    operation_description='생성된 이미지를 삭제합니다.',
    tags=['backgrounds'],
    responses={
        204: "No Content",
        404: "Background not found.",
    }
)
@api_view(['GET', 'PUT', 'DELETE'])
def background_manage(request, backgroundId):
    try:
        background = Background.objects.get(id=backgroundId)
    except Background.DoesNotExist:
        return Response({"error": "해당 배경 이미지가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = BackgroundSerializer(background)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        user = background.user
        image = background.image
        gen_type = background.gen_type
        try:
            concept_option = json.loads(background.concept_option)
        except json.JSONDecodeError as e:
            logger.error("JSONDecodeError: %s", e)
            concept_option = {}  # 기본값 설정

        output_w = background.output_w
        output_h = background.output_h

        image_url = image.image_url
        try:
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            image_file = io.BytesIO(image_response.content)
            logger.debug("Downloaded image from URL: %s", image_url)
        except requests.RequestException as e:
            logger.error("Failed to download image: %s", e)
            return Response({"error": "Failed to download image"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        url = "https://api.draph.art/v1/generate/"
        headers = {'Authorization': f'Bearer {settings.DRAPHART_API_KEY}'}
        files = {
            'image': ('image.jpg', image_file, 'image/jpeg')
        }
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

        if response.status_code != 200:
            logger.debug("AI 이미지 생성 실패: %s", response.text)
            return Response({"error": "AI 이미지 생성 실패", "details": response.text}, status=status.HTTP_400_BAD_REQUEST)

        response_data = response.content

        try:
            image_data = base64.b64decode(response_data)
            image_bytes = io.BytesIO(image_data)
            pil_image = PILImage.open(image_bytes)
            pil_image = pil_image.convert('RGB')
            png_image_bytes = io.BytesIO()
            pil_image.save(png_image_bytes, format='PNG')
            png_image_bytes.seek(0)

            s3 = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME)
            unique_filename = f"{uuid.uuid4()}.png"
            s3.upload_fileobj(png_image_bytes, settings.AWS_STORAGE_BUCKET_NAME, unique_filename, ExtraArgs={'ContentType': 'image/png'})
            s3_url = f"http://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{unique_filename}"

        except Exception as e:
            logger.error("Error uploading to S3: %s", e)
            return Response({"error": "Failed to upload image to S3", "details": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        background.image_url = s3_url
        background.recreated = True
        background.save()

        serializer = BackgroundSerializer(background)
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        s3 = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME)
        file_key = background.image_url.split('/')[-1]
        try:
            s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key)
        except Exception as e:
            logger.error("S3 파일 삭제 오류: %s", e)
            return Response({"error": "S3 파일 삭제 오류", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        background.delete()
        return Response({"message": "Image deleted successfully."}, status=status.HTTP_200_OK)
