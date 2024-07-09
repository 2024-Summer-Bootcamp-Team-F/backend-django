from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, serializers
from rest_framework.decorators import api_view, parser_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
import boto3
from django.conf import settings
import logging

from .models import Image
from .serializers import ImageSerializer

logger = logging.getLogger(__name__)

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
    serializer = ImageSerializer(data=request.data, context={'request': request})
    # 유효성 검사
    try:
        serializer.is_valid(raise_exception=True)
    except serializers.ValidationError as e:
        logger.error("Validation error: ", e)
        error_message = {
            "error": e.detail,
        }
        return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()  # 데이터 저장
    return Response({"success": "이미지가 성공적으로 업로드되었습니다.", "data": serializer.data}, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='get',
    operation_id='이미지 조회',
    operation_description='이미지를 조회합니다.',
    tags=['Images'],
    responses={
        200: ImageSerializer,
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
def image_manage(request, image_id):
    """
    이미지 조회 및 삭제 뷰셋
    """
    try:
        image = Image.objects.get(id=image_id)  # 이미지 객체를 데이터베이스에서 가져옴
    except Image.DoesNotExist:
        return Response({"error": "해당 이미지를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)  # 이미지가 없으면 404 응답

    if request.method == 'GET':
        serializer = ImageSerializer(image)  # 이미지 객체를 시리얼라이즈
        return Response({"success": "이미지가 성공적으로 조회되었습니다.", "data": serializer.data}, status=status.HTTP_200_OK)  # 성공 응답

    elif request.method == 'DELETE':
        # S3에서 파일 삭제
        s3 = boto3.client('s3', region_name=settings.AWS_S3_REGION_NAME)
        file_key = image.image_url.split('/')[-1]
        s3.delete_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=file_key)

        # 데이터베이스에서 이미지 삭제
        image.delete()
        return Response({"success": "이미지가 성공적으로 삭제되었습니다."}, status=status.HTTP_200_OK)  # 성공적으로 삭제되었음을 나타내는 200 응답
