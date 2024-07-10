import requests
import base64
import io
import json
import boto3
from PIL import Image as PILImage
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import BackgroundImage
from .serializers import BackgroundImageSerializer
from user.models import User
from image.models import Image
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import logging
import tempfile
import uuid

logger = logging.getLogger(__name__)

GEN_TYPES = ['remove_bg', 'color_bg', 'simple', 'concept']

@swagger_auto_schema(
    method='post',
    operation_id='AI 배경 이미지 생성',
    operation_description='외부 API를 호출하여 AI 배경 이미지를 생성합니다.',
    tags=['Background'],
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='사용자 ID'),
            'image_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='이미지 ID'),
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='API 제공 사이트의 사용자 이름'),
            'gen_type': openapi.Schema(type=openapi.TYPE_STRING, description='배경 타입', enum=GEN_TYPES),
            'multiblob_sod': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='상품이 한개인지 여러개인지에 대한 옵션', default=False),
            'output_h': openapi.Schema(type=openapi.TYPE_INTEGER, description='이미지 높이', default=1000),
            'output_w': openapi.Schema(type=openapi.TYPE_INTEGER, description='이미지 너비', default=1000),
            'bg_color_hex_code': openapi.Schema(type=openapi.TYPE_STRING, description='단색 배경 RGB의 hex 코드', default="#FFFFFF"),
            'concept_option': openapi.Schema(type=openapi.TYPE_STRING, description='테마, 카테고리, 결과 이미지 개수 옵션 (유효한 JSON 문자열)'),
        },
        required=['user_id', 'image_id', 'username', 'gen_type']
    ),
    responses={
        201: BackgroundImageSerializer,
        400: "Bad request. Make sure to provide valid input.",
        404: "User or Image not found.",
        500: "External API error.",
    }
)
@api_view(['POST'])
def generate_background(request):
    """
    외부 API를 호출하여 AI 배경 이미지를 생성합니다.
    """
    user_id = request.data.get('user_id')
    image_id = request.data.get('image_id')
    username = request.data.get('username')
    gen_type = request.data.get('gen_type')
    multiblob_sod = request.data.get('multiblob_sod', False)
    output_h = request.data.get('output_h', 1000)
    output_w = request.data.get('output_w', 1000)
    bg_color_hex_code = request.data.get('bg_color_hex_code', '#FFFFFF')
    concept_option = request.data.get('concept_option', '')

    if not (user_id and image_id and username and gen_type):
        return Response({"error": "필수 입력값(user_id, image_id, username, gen_type)이 필요합니다."}, status=status.HTTP_400_BAD_REQUEST)

    if gen_type not in GEN_TYPES:
        return Response({"error": f"유효하지 않은 gen_type입니다. 가능한 값: {', '.join(GEN_TYPES)}"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({"error": "해당 사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    try:
        image = Image.objects.get(id=image_id)
    except Image.DoesNotExist:
        return Response({"error": "해당 이미지를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    # 이미지 파일 다운로드
    image_url = image.image_url  # S3 URL
    try:
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        image_file = io.BytesIO(image_response.content)
    except requests.exceptions.RequestException as e:
        logger.error(f"이미지 다운로드 실패: {str(e)}")
        return Response({"error": "이미지 다운로드 실패"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 외부 API 호출
    api_url = 'https://api.draph.art/v1/generate/'  # 드랩아트 API 엔드포인트
    headers = {'Authorization': f'Bearer {settings.DRAPHART_API_KEY}'}

    files = {
        'image': ('image.jpg', image_file, 'image/jpeg'),
    }
    data = {
        'username': username,
        'gen_type': gen_type,
        'multiblob_sod': multiblob_sod,
        'output_h': output_h,
        'output_w': output_w,
        'bg_color_hex_code': bg_color_hex_code,
        'concept_option': concept_option,
    }

    response = requests.post(api_url, headers=headers, files=files, data=data)

    if response.status_code != 200:
        logger.error(f"외부 API 호출 실패: {response.status_code}, {response.text}")
        return Response({"error": "외부 API 호출에 실패했습니다."}, status=response.status_code)

    # 디버깅을 위해 반환된 데이터 로그 출력
    logger.debug(f"외부 API 응답 데이터: {response.content[:100]}...")  # 첫 100바이트만 로그에 출력

    response_data = response.content

    # base64 디코딩
    try:
        image_data = base64.b64decode(response_data)
        image_bytes = io.BytesIO(image_data)
        pil_image = PILImage.open(image_bytes)
        pil_image = pil_image.convert("RGB")  # 이미지 형식을 PNG로 변환
        png_image_bytes = io.BytesIO()
        pil_image.save(png_image_bytes, format="PNG")
        png_image_bytes.seek(0)  # 파일 포인터를 시작 위치로 되돌림

        s3 = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME)
        unique_filename = f"{uuid.uuid4()}.png"
        s3.upload_fileobj(png_image_bytes, settings.AWS_STORAGE_BUCKET_NAME, unique_filename, ExtraArgs={'ContentType': 'image/png'})

        s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{unique_filename}"

    except Exception as e:
        logger.error(f"S3 업로드 실패: {str(e)}")
        return Response({"error": f"S3 업로드 실패: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 데이터베이스에 배경 이미지 저장
    background_image = BackgroundImage.otbjecs.create(
        user=user,
        image=image,
        gen_type=gen_type,
        concept_option=concept_option,
        output_h=output_h,
        output_w=output_w,
        image_url=s3_url
    )

    serializer = BackgroundImageSerializer(background_image)
    return Response({"success": "AI 배경 이미지가 성공적으로 생성되었습니다.", "data": serializer.data}, status=status.HTTP_201_CREATED)
