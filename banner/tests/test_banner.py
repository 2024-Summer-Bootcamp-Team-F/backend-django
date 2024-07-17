import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

@pytest.mark.integration
@pytest.mark.django_db
class TestBannerAPI:
    def setup_method(self):
        self.client = APIClient()
        self.create_banner_url = reverse('create_banner')

    def test_banner_creation(self):
        response = self.client.post(self.create_banner_url, {'image_id': 1, 'ad_text': 'Sample Ad'})
        assert response.status_code == status.HTTP_201_CREATED
