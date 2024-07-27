from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import Video
from .serializers import VideoSerializer
from background.models import Background
from .tasks import generate_video_task
import uuid
from django.conf import settings

@swagger_auto_schema(method='post',
                     request_body=openapi.Schema(
                         type=openapi.TYPE_OBJECT,
                         properties={
                             'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the user'),
                             'background_id': openapi.Schema(type=openapi.TYPE_INTEGER,
                                                             description='ID of the background'),
                         }
                     ),
                     responses={201: openapi.Response('Created', openapi.Schema(
                         type=openapi.TYPE_OBJECT,
                         properties={
                             'video_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                             'video_url': openapi.Schema(type=openapi.TYPE_STRING)
                         }
                     ))})
@api_view(['POST'])
def videos_create(request):
    user_id = request.data.get('user_id')
    background_id = request.data.get('background_id')

    try:
        background = Background.objects.get(id=background_id)
    except Background.DoesNotExist:
        return Response({"error": "Background not found"}, status=status.HTTP_404_NOT_FOUND)

    unique_filename = f"videos/{uuid.uuid4()}.mp4"
    s3_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{unique_filename}"

    video = Video.objects.create(user_id=user_id, background=background, video_url=s3_url)
    generate_video_task.delay(video.id, background.image_url, unique_filename)

    return Response({'video_id': video.id, 'video_url': s3_url}, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT', 'DELETE'])
def video_manage(request, videoId):
    try:
        video = Video.objects.get(id=videoId)
    except Video.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = VideoSerializer(video)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = VideoSerializer(video, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        video.is_deleted = True
        video.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
