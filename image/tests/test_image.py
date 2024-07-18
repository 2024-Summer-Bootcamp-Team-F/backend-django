import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from user.models import User
from image.models import Image
import os

@pytest.mark.integration
@pytest.mark.django_db
class TestImageAPI:
    def setup_method(self):
        self.client = APIClient()
        self.upload_image_url = reverse('upload-image')
        self.user = User.objects.create(nickname='testuser')

    def read_image_with_correct_encoding(self, file_path):
        with open(file_path, 'rb') as f:  # 이미지 파일은 바이너리 모드로 읽어야 합니다
            content = f.read()
        return content

    def test_image_upload(self): #이미지 업로드
        file_path = 'test_image.jpg'  # 테스트용 이미지 파일 경로
        with open(file_path, 'rb') as f:
            image_data = f.read()

        response = self.client.post(self.upload_image_url, {'file': image_data, 'user_id': self.user.id}, format='multipart')
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert 'image_id' in response.data

    def test_image_upload_no_file(self): #파일 없이 업로드
        response = self.client.post(self.upload_image_url, {'user_id': self.user.id}, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_image_upload_invalid_user(self): #잘못된 사용자 ID로 업로드
        file_path = 'test_image.jpg'
        with open(file_path, 'rb') as f:
            image_data = f.read()

        response = self.client.post(self.upload_image_url, {'file': image_data, 'user_id': 999}, format='multipart')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_get_image(self): #이미지 조회 --> 기존 업로드 이미지 조회했을 때 올바른 데이터 반환하는지 테스트
        image = Image.objects.create(user=self.user, image_url='http://testserver/media/test_image.jpg')
        get_image_url = reverse('image-detail', kwargs={'image_id': image.id})
        response = self.client.get(get_image_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['image_url'] == image.image_url

    def test_get_nonexistent_image(self): #존재하지 않는 이미지 조회
        get_image_url = reverse('image-detail', kwargs={'image_id': 999})
        response = self.client.get(get_image_url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_image(self): #이미지 삭제
        image = Image.objects.create(user=self.user, image_url='http://testserver/media/test_image.jpg')
        delete_image_url = reverse('image-detail', kwargs={'image_id': image.id})
        response = self.client.delete(delete_image_url)
        assert response.status_code == status.HTTP_200_OK
        assert Image.objects.filter(id=image.id).count() == 0

    def test_delete_nonexistent_image(self): #존재하지 않는 이미지 삭제
        delete_image_url = reverse('image-detail', kwargs={'image_id': 999})
        response = self.client.delete(delete_image_url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
