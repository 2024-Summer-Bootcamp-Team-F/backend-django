#1. @patch('requests.get'): requests.get 함수를 모의(mock) 처리하여 실제 HTTP 요청을 보내지 않고도 테스트를 수행
#2.모의 응답 설정: mock_response.content에 가짜 이미지 데이터를 설정하고, mock_response.raise_for_status 메서드를 모의 처리
#3.다양한 테스트 케이스: 각 테스트 케이스는 배경 이미지와 재생성된 배경 이미지의 리사이징, 잘못된 데이터 처리, 존재하지 않는 ID 처리 등을 포함



import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch, MagicMock
from background.models import Background
from recreated_background.models import RecreatedBackground

@pytest.mark.integration  # 이 테스트가 통합 테스트임을 나타냅니다.
@pytest.mark.django_db  # 이 테스트가 데이터베이스 접근이 필요함을 나타냅니다.
class TestImageResizingAPI:
    def setup_method(self):
        # 각 테스트 메서드가 실행되기 전에 호출되는 설정 메서드입니다.
        self.client = APIClient()
        self.resize_background_image_url = reverse('resize-background-image')  # 배경 이미지 리사이징 URL
        self.resize_recreated_background_image_url = reverse('resize-recreated-background-image')  # 재생성된 배경 이미지 리사이징 URL
        # 테스트에 사용할 샘플 배경 이미지를 생성합니다.
        self.background = Background.objects.create(image_url='http://example.com/background.jpg')
        # 테스트에 사용할 샘플 재생성된 배경 이미지를 생성합니다.
        self.recreated_background = RecreatedBackground.objects.create(image_url='http://example.com/recreated_background.jpg')

    @patch('requests.get')  # requests.get 함수를 모의(mock) 처리합니다.
    def test_resize_background_image(self, mock_get):
        # 모의 HTTP 응답을 설정합니다.
        mock_response = MagicMock()
        mock_response.content = b'fake image data'  # 가짜 이미지 데이터
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        data = {
            'width': 100,
            'height': 100,
            'background_id': self.background.id
        }
        # POST 요청을 보내서 배경 이미지를 리사이징합니다.
        response = self.client.post(self.resize_background_image_url, data, format='json')
        # 상태 코드가 200 OK 인지 확인합니다.
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        # 응답 데이터에 특정 필드들이 포함되어 있는지 확인합니다.
        assert 'resized_image_url' in response_data
        assert 'id' in response_data

    @patch('requests.get')  # requests.get 함수를 모의(mock) 처리합니다.
    def test_resize_recreated_background_image(self, mock_get):
        # 모의 HTTP 응답을 설정합니다.
        mock_response = MagicMock()
        mock_response.content = b'fake image data'  # 가짜 이미지 데이터
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        data = {
            'width': 100,
            'height': 100,
            'recreated_background_id': self.recreated_background.id
        }
        # POST 요청을 보내서 재생성된 배경 이미지를 리사이징합니다.
        response = self.client.post(self.resize_recreated_background_image_url, data, format='json')
        # 상태 코드가 200 OK 인지 확인합니다.
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        # 응답 데이터에 특정 필드들이 포함되어 있는지 확인합니다.
        assert 'resized_image_url' in response_data
        assert 'id' in response_data

    @patch('requests.get')  # requests.get 함수를 모의(mock) 처리합니다.
    def test_resize_background_image_invalid_data(self, mock_get):
        # 모의 HTTP 응답을 설정합니다.
        mock_response = MagicMock()
        mock_response.content = b'fake image data'  # 가짜 이미지 데이터
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        data = {
            'width': -100,  # 유효하지 않은 가로 길이
            'height': 100,
            'background_id': self.background.id
        }
        # POST 요청을 보내서 배경 이미지를 리사이징합니다.
        response = self.client.post(self.resize_background_image_url, data, format='json')
        # 상태 코드가 400 Bad Request 인지 확인합니다.
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @patch('requests.get')  # requests.get 함수를 모의(mock) 처리합니다.
    def test_resize_recreated_background_image_not_found(self, mock_get):
        # 모의 HTTP 응답을 설정합니다.
        mock_response = MagicMock()
        mock_response.content = b'fake image data'  # 가짜 이미지 데이터
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        data = {
            'width': 100,
            'height': 100,
            'recreated_background_id': 99999  # 존재하지 않는 ID
        }
        # POST 요청을 보내서 재생성된 배경 이미지를 리사이징합니다.
        response = self.client.post(self.resize_recreated_background_image_url, data, format='json')
        # 상태 코드가 404 Not Found 인지 확인합니다.
        assert response.status_code == status.HTTP_404_NOT_FOUND
