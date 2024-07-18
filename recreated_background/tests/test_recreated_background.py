import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from background.models import Background
from recreated_background.models import RecreatedBackground
from user.models import User
from image.models import Image
import uuid

@pytest.mark.integration
@pytest.mark.django_db
class TestRecreatedBackgroundAPI:
    def setup_method(self):
        self.client = APIClient()
        self.recreate_url = reverse('recreated-backgrounds')
        self.user = User.objects.create(nickname='testuser')
        self.image = Image.objects.create(user=self.user, image_url='http://testserver/media/test_image.jpg')
        self.background = Background.objects.create(
            user=self.user,
            image=self.image,
            gen_type='simple',
            concept_option='{"category": "cosmetics", "theme": "modern", "num_results": 1}',
            output_w=1000,
            output_h=1000,
            image_url='http://testserver/media/test_background.png'
        )

    def test_recreate_background(self): #배경 이미지 재생성 테스트
        payload = {
            'concept_option': {
                'category': 'cosmetics',
                'theme': 'modern',
                'num_results': 1
            }
        }
        response = self.client.post(self.recreate_url, payload, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'image_url' in response.data

    def test_get_recreated_background(self): #재생성된 배경 이미지 조회 테스트
        recreated_background = RecreatedBackground.objects.create(
            background=self.background,
            concept_option='{"category": "cosmetics", "theme": "modern", "num_results": 1}',
            image_url='http://testserver/media/test_recreated_background.png'
        )
        get_recreated_background_url = reverse('recreated-background-manage', kwargs={'recreated_background_id': recreated_background.id})
        response = self.client.get(get_recreated_background_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['image_url'] == recreated_background.image_url

    def test_delete_recreated_background(self): #재생성된 배경 이미지 삭제 테스트
        recreated_background = RecreatedBackground.objects.create(
            background=self.background,
            concept_option='{"category": "cosmetics", "theme": "modern", "num_results": 1}',
            image_url='http://testserver/media/test_recreated_background.png'
        )
        delete_recreated_background_url = reverse('recreated-background-manage', kwargs={'recreated_background_id': recreated_background.id})
        response = self.client.delete(delete_recreated_background_url)
        assert response.status_code == status.HTTP_200_OK
        assert RecreatedBackground.objects.filter(id=recreated_background.id).count() == 0

    def test_get_nonexistent_recreated_background(self): #존재하지 않는 재생성된 배경 이미지 조회 테스트
        get_recreated_background_url = reverse('recreated-background-manage', kwargs={'recreated_background_id': uuid.uuid4()})
        response = self.client.get(get_recreated_background_url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_recreated_background(self): #존재하지 않는 재생성된 배경 이미지 삭제 테스트
        delete_recreated_background_url = reverse('recreated-background-manage', kwargs={'recreated_background_id': uuid.uuid4()})
        response = self.client.delete(delete_recreated_background_url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
