import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

@pytest.mark.integration
@pytest.mark.django_db
class TestBackgroundAPI:
    def setup_method(self):
        self.client = APIClient()
        self.backgrounds_url = reverse('backgrounds')

    def test_background_creation(self):
        response = self.client.post(self.backgrounds_url, {'param': 'value'})
        assert response.status_code == status.HTTP_201_CREATED
