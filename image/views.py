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
    try:
        serializer.is_valid(raise_exception=True)
    except serializers.ValidationError as e:
        logger.error("Validation error: ", e)
        error_message = {
            "error": e.detail,
        }
        return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

    serializer.save()
    return Response({"success": "이미지가 성공적으로 업로드되었습니다.", "data": serializer.data}, status=status.HTTP_201_CREATED)
