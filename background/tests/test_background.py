import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from user.models import User
from image.models import Image
from background.models import Background
import uuid

@pytest.mark.integration
@pytest.mark.django_db
class TestBackgroundAPI:
    def setup_method(self):
        self.client = APIClient()
        self.backgrounds_url = reverse('backgrounds')
        self.user = User.objects.create(nickname='testuser')
        self.image = Image.objects.create(user=self.user, image_url='http://testserver/media/test_image.jpg')

    def test_background_creation(self): #배경 이미지 생성 테스트
        payload = {
            'user_id': self.user.id,
            'image_id': self.image.id,
            'gen_type': 'simple',
            'output_w': 1000,
            'output_h': 1000,
            'concept_option': {
                'category': 'cosmetics',
                'theme': 'modern',
                'num_results': 1
            }
        }
        response = self.client.post(self.backgrounds_url, payload, format='json')
        assert response.status_code == status.HTTP_202_ACCEPTED
        assert 'task_id' in response.data
        assert 's3_url' in response.data

    def test_get_background(self): #배경 이미지 조회 테스트
        background = Background.objects.create(
            user=self.user,
            image=self.image,
            gen_type='simple',
            concept_option='{"category": "cosmetics", "theme": "modern", "num_results": 1}',
            output_w=1000,
            output_h=1000,
            image_url='http://testserver/media/test_background.png'
        )
        get_background_url = reverse('background-manage', kwargs={'background_id': background.id})
        response = self.client.get(get_background_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['image_url'] == background.image_url

    def test_update_background(self): #배경 이미지 수정 테스트
        background = Background.objects.create(
            user=self.user,
            image=self.image,
            gen_type='simple',
            concept_option='{"category": "cosmetics", "theme": "modern", "num_results": 1}',
            output_w=1000,
            output_h=1000,
            image_url='http://testserver/media/test_background.png'
        )
        update_background_url = reverse('background-manage', kwargs={'background_id': background.id})
        response = self.client.put(update_background_url)
        assert response.status_code == status.HTTP_200_OK
        assert 'image_url' in response.data

    def test_delete_background(self): #배경 이미지 삭제 테스트
        background = Background.objects.create(
            user=self.user,
            image=self.image,
            gen_type='simple',
            concept_option='{"category": "cosmetics", "theme": "modern", "num_results": 1}',
            output_w=1000,
            output_h=1000,
            image_url='http://testserver/media/test_background.png'
        )
        delete_background_url = reverse('background-manage', kwargs={'background_id': background.id})
        response = self.client.delete(delete_background_url)
        assert response.status_code == status.HTTP_200_OK
        assert Background.objects.filter(id=background.id).count() == 0

    def test_get_nonexistent_background(self): #존재하지 않는 배경 이미지 조회 테스트
        get_background_url = reverse('background-manage', kwargs={'background_id': uuid.uuid4()})
        response = self.client.get(get_background_url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_nonexistent_background(self): #존재하지 않는 배경 이미지 수정 테스트
        update_background_url = reverse('background-manage', kwargs={'background_id': uuid.uuid4()})
        response = self.client.put(update_background_url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_nonexistent_background(self): #존재하지 않는 배경 이미지 삭제 테스트
        delete_background_url = reverse('background-manage', kwargs={'background_id': uuid.uuid4()})
        response = self.client.delete(delete_background_url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
