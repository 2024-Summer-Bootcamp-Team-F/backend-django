from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from user.models import User
from texttovideo.models import TextToVideo

class TextToVideoTests(APITestCase):

    def setUp(self):
        # 사용자 생성 메서드 정의
        self.user = User.objects.create(nickname='testuser')
        self.create_url = reverse('create_video')
        self.handle_url = lambda video_id: reverse('handle_video', args=[video_id])

    def test_create_video(self):
        # 비디오 생성 테스트
        data = {
            'prompt': 'A rocket flying that is about to take off',
            'user_id': self.user.id
        }
        response = self.client.post(self.create_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        self.assertIn('prompt', response.data)
        self.assertIn('video_url', response.data)

    def test_get_video(self):
        # 비디오 조회 테스트
        video = TextToVideo.objects.create(prompt='A rocket flying that is about to take off', video_url='https://storage.googleapis.com/example.mp4', user=self.user)
        url = self.handle_url(video.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], video.id)
        self.assertEqual(response.data['prompt'], video.prompt)
        self.assertEqual(response.data['video_url'], video.video_url)

    def test_delete_video(self):
        # 비디오 삭제 테스트
        video = TextToVideo.objects.create(prompt='A rocket flying that is about to take off', video_url='https://storage.googleapis.com/example.mp4', user=self.user)
        url = self.handle_url(video.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], '삭제 성공')
        # 비디오가 실제로 삭제되었는지 확인
        with self.assertRaises(TextToVideo.DoesNotExist):
            TextToVideo.objects.get(id=video.id)

