import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
import chardet


@pytest.mark.integration
@pytest.mark.django_db
class TestImageAPI:
    def setup_method(self):
        self.client = APIClient()
        self.upload_image_url = reverse('upload-image')

    def read_image_with_correct_encoding(self, file_path):
        # 파일의 인코딩 감지
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result['encoding']

        # 감지된 인코딩을 사용하여 파일 읽기
        with open(file_path, 'rb') as f:  # 이미지 파일은 바이너리 모드로 읽어야 합니다
            content = f.read()
        return content

    def test_image_upload(self):
        file_path = 'test_image.jpg'
        image_data = self.read_image_with_correct_encoding(file_path)
        response = self.client.post(self.upload_image_url, {'image': image_data}, format='multipart')
        assert response.status_code == status.HTTP_201_CREATED
