from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, serializers
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import boto3
from django.conf import settings
import logging
import base64
from .models import Image
from .serializers import ImageSerializer, ImageDetailSerializer
from .tasks import upload_image_to_s3

# 로깅 설정
logger = logging.getLogger(__name__)

# Swagger를 사용하여 이미지 업로드 API 문서화
@swagger_auto_schema(
    method='post',
    operation_id='이미지 업로드',
    operation_description='이미지를 업로드합니다.',
    tags=['Images'],
    request_body=ImageSerializer,
    responses={
        201: "Image successfully uploaded.",
        400: "Bad request. Make sure to provide a valid image.",
    }
)
@api_view(['POST'])
@parser_classes([MultiPartParser, FormParser])
def upload_image(request, *args, **kwargs):
    """
    이미지 업로드
    """
    # 요청 데이터를 시리얼라이즈
    serializer = ImageSerializer(data=request.data, context={'request': request})
    try:
        serializer.is_valid(raise_exception=True)
    except serializers.ValidationError as e:
        # 유효성 검증 오류 로그 기록
        logger.error("Validation error: %s", e)
        error_message = {
            "error": e.detail,
        }
        return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

    # 파일과 사용자 ID 추출
    file = request.FILES['file']
    user_id = request.data.get('user_id')
    content_type = file.content_type  # 파일의 content_type을 가져옴
    file_content = base64.b64encode(file.read()).decode('utf-8')  # 파일 내용을 base64로 인코딩하여 전달

    # 이미지 인스턴스 생성
    image_instance = Image.objects.create(user_id=user_id, image_url='')

    # 비동기로 S3 업로드
    logger.info(f"Calling Celery task for uploading file: {file.name}")
    # Celery 태스크 호출
    result = upload_image_to_s3.delay(file.name, file_content, content_type, image_instance.id)
    logger.info(f"Celery task called with ID: {result.id}")

    return Response({
        "success": "이미지가 업로드 중입니다. 업로드가 완료되면 URL이 업데이트됩니다.",
        "image_id": image_instance.id  # image_id 반환
    }, status=status.HTTP_202_ACCEPTED)

# Swagger를 사용하여 이미지 조회 및 삭제 API 문서화
@swagger_auto_schema(
    method='get',
    operation_id='이미지 조회',
    operation_description='이미지를 조회합니다.',
    tags=['Images'],
    responses={
        200: ImageDetailSerializer,  # 응답에 ImageDetailSerializer 사용
        404: "Image not found.",
    }
)
@swagger_auto_schema(
    method='delete',
    operation_id='이미지 삭제',
    operation_description='이미지를 삭제합니다.',
    tags=['Images'],
    responses={
        204: "Image successfully deleted.",
        404: "Image not found.",
    }
)
@api_view(['GET', 'DELETE'])
def image_manage(request, imageId):
    """
    이미지 조회 및 삭제 뷰셋
    """
    # 이미지 객체를 데이터베이스에서 가져옴
    try:
        image = Image.objects.get(id=imageId)
    except Image.DoesNotExist:
        # 이미지가 없으면 404 응답
        return Response({"error": "해당 이미지를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # 이미지 객체를 시리얼라이즈
        serializer = ImageDetailSerializer(image)  # ImageDetailSerializer 사용
        # 성공 응답
        return Response({"success": "이미지가 성공적으로 조회되었습니다.", "data": serializer.data}, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        # S3에서 파일 삭제
        s3 = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME)
        file_key = image.image_url.split('/')[-1]
        s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key)

        # 데이터베이스에서 이미지 삭제
        image.delete()
        # 성공적으로 삭제되었음을 나타내는 200 응답
        return Response({"success": "이미지가 성공적으로 삭제되었습니다."}, status=status.HTTP_200_OK)