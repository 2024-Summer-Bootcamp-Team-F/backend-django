import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

@pytest.mark.integration
@pytest.mark.django_db
class TestImageResizingAPI:
    def setup_method(self):
        self.client = APIClient()
        self.resize_url = reverse('resize-background-image')

    def test_image_resizing(self):
        response = self.client.post(self.resize_url, {'image_id': 1, 'width': 100, 'height': 100})
        assert response.status_code == status.HTTP_200_OK
