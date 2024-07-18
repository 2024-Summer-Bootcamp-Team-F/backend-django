# test_banner.py

import pytest
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from user.models import User
from image.models import Image
from .models import Banner

@pytest.mark.django_db
class BannerAPITests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.image = Image.objects.create(url='http://example.com/image.jpg')
        self.banner_data = {
            'item_name': 'Test Item',
            'item_concept': 'Test Concept',
            'item_category': 'Test Category',
            'add_information': 'Test Information',
            'image_id': self.image.id,
            'user_id': self.user.id
        }
        self.banner = Banner.objects.create(
            item_name='Existing Item',
            item_concept='Existing Concept',
            item_category='Existing Category',
            ad_text='Existing Ad Text',
            serve_text='Existing Serve Text',
            ad_text2='Existing Ad Text 2',
            serve_text2='Existing Serve Text 2',
            add_information='Existing Information',
            user_id=self.user,
            image_id=self.image
        )

    def test_create_banner(self):
        url = reverse('create_banner')
        response = self.client.post(url, self.banner_data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data['data']

    def test_get_banner(self):
        url = reverse('handle_banner', args=[self.banner.id])
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['item_name'] == self.banner.item_name

    def test_update_banner(self):
        url = reverse('handle_banner', args=[self.banner.id])
        updated_data = self.banner_data.copy()
        updated_data['item_name'] = 'Updated Item'
        response = self.client.put(url, updated_data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['data']['item_name'] == 'Updated Item'

    def test_delete_banner(self):
        url = reverse('handle_banner', args=[self.banner.id])
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_200_OK
        assert not Banner.objects.filter(id=self.banner.id).exists()

    def test_get_nonexistent_banner(self):
        url = reverse('handle_banner', args=[9999])
        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_nonexistent_banner(self):
        url = reverse('handle_banner', args=[9999])
        response = self.client.put(url, self.banner_data, format='json')
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_banner(self):
        url = reverse('handle_banner', args=[9999])
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND