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
from image.models import Image

@swagger_auto_schema(method='post',
                     request_body=openapi.Schema(
                         type=openapi.TYPE_OBJECT,
                         properties={
                             'user_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the user'),
                             'image_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the image'),
                             'text_prompt': openapi.Schema(type=openapi.TYPE_STRING, description='Text prompt for video generation'),
                         }
                     ),
                     responses={201: openapi.Response('Created', openapi.Schema(
                         type=openapi.TYPE_OBJECT,
                         properties={
                             'video_id': openapi.Schema(type=openapi.TYPE_INTEGER)
                         }
                     ))})
@api_view(['POST'])
def videos_create(request):
    user_id = request.data.get('user_id')
    image_id = request.data.get('image_id')
    text_prompt = request.data.get('text_prompt')

    if not text_prompt:
        return Response({"error": "Text prompt is required"}, status=status.HTTP_400_BAD_REQUEST)

    try:
        image = Image.objects.get(id=image_id)
    except Background.DoesNotExist:
        return Response({"error": "Background not found"}, status=status.HTTP_404_NOT_FOUND)

    video = Video.objects.create(user_id=user_id, image=image)
    unique_filename = f"{uuid.uuid4()}.mp4"
    generate_video_task.delay(video.id, image.image_url, unique_filename, text_prompt)

    return Response({'video_id': video.id}, status=status.HTTP_201_CREATED)

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
