# user/tests/test_user.py

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

@pytest.mark.integration
@pytest.mark.django_db
class TestUserAPI:
    def setup_method(self):
        self.client = APIClient()
        self.create_nickname_url = reverse('user:create-nickname')

    def test_create_nickname(self):  # 이름을 test_create_nickname으로 변경
        response = self.client.post(self.create_nickname_url, {'nickname': 'testuser'})
        assert response.status_code == status.HTTP_201_CREATED
