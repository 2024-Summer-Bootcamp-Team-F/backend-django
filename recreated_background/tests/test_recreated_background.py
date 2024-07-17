import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

@pytest.mark.integration
@pytest.mark.django_db
class TestRecreatedBackgroundAPI:
    def setup_method(self):
        self.client = APIClient()
        self.recreate_url = reverse('recreated-backgrounds')

    def test_recreate_background(self):
        response = self.client.post(self.recreate_url, {'image_id': 1, 'parameters': {}})
        assert response.status_code == status.HTTP_200_OK
