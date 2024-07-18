import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from user.models import User


@pytest.mark.integration
@pytest.mark.django_db
class TestUserAPI:
    def setup_method(self):
        self.client = APIClient()
        self.create_nickname_url = reverse('user:create-nickname')

    def test_create_nickname(self):
        response = self.client.post(self.create_nickname_url, {'nickname': 'testuser'})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['data']['nickname'] == 'testuser'

    def test_create_nickname_duplicate(self): #닉네임 중복 검사
        self.client.post(self.create_nickname_url, {'nickname': 'testuser'})
        response = self.client.post(self.create_nickname_url, {'nickname': 'testuser'})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_create_nickname_blank(self): #닉네임 공백 검사
        response = self.client.post(self.create_nickname_url, {'nickname': ''})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'error' in response.data

    def test_get_nickname(self): #닉네임 조회 테스트
        create_response = self.client.post(self.create_nickname_url, {'nickname': 'testuser'})
        user_id = create_response.data['data']['id']
        get_nickname_url = reverse('user:get-nickname', kwargs={'user_id': user_id})
        get_response = self.client.get(get_nickname_url)
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.data['data']['nickname'] == 'testuser'

    def test_get_nonexistent_nickname(self): #존재하지 않는 유저 닉네임 조회
        get_nickname_url = reverse('user:get-nickname', kwargs={'user_id': 999})
        response = self.client.get(get_nickname_url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_nickname_deleted_user(self): #삭제된 유저 닉네임 조회
        create_response = self.client.post(self.create_nickname_url, {'nickname': 'testuser'})
        user_id = create_response.data['data']['id']
        User.objects.filter(id=user_id).update(is_deleted=True)
        get_nickname_url = reverse('user:get-nickname', kwargs={'user_id': user_id})
        response = self.client.get(get_nickname_url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
