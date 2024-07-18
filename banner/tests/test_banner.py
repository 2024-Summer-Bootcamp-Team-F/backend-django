import pytest
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from user.models import User
from image.models import Image
from banner.models import Banner

# 데이터베이스와의 상호작용을 테스트하기 위해 pytest를 사용
@pytest.mark.django_db
class BannerAPITests(APITestCase):

    # 각 테스트 전에 실행되는 설정 메서드
    def setUp(self):
        self.client = APIClient()                                                       # API 클라이언트 인스턴스 생성
        self.user = User.objects.create_user(username='testuser', password='testpass')  # 테스트 사용자 생성
        self.image = Image.objects.create(url='http://example.com/image.jpg')           # 테스트 이미지 객체 생성
        self.banner_data = {                                                            # 배너 생성에 사용할 데이터 설정
            'item_name': 'Test Item',
            'item_concept': 'Test Concept',
            'item_category': 'Test Category',
            'add_information': 'Test Information',
            'image_id': self.image.id,
            'user_id': self.user.id
        }
        self.banner = Banner.objects.create(                                            # 기존 배너 객체 생성
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

    # 배너 생성 테스트
    def test_create_banner(self):
        url = reverse('create_banner')                                                  # 배너 생성 엔드포인트 URL 생성
        response = self.client.post(url, self.banner_data, format='json')               # 배너 생성 요청 전송
        assert response.status_code == status.HTTP_201_CREATED                          # 응답 상태 코드가 201(Created)인지 확인
        assert 'id' in response.data['data']                                            # 응답 데이터에 'id'가 포함되어 있는지 확인

    # 배너 조회 테스트
    def test_get_banner(self):
        url = reverse('handle_banner', args=[self.banner.id])                   # 배너 조회 엔드포인트 URL 생성
        response = self.client.get(url)                                                  # 배너 조회 요청 전송
        assert response.status_code == status.HTTP_200_OK                                # 응답 상태 코드가 200(OK)인지 확인
        assert response.data['data']['item_name'] == self.banner.item_name               # 응답 데이터의 'item_name'이 기존 배너의 'item_name'과 일치하는지 확인

    # 배너 업데이트 테스트
    def test_update_banner(self):
        url = reverse('handle_banner', args=[self.banner.id])                   # 배너 업데이트 엔드포인트 URL 생성
        updated_data = self.banner_data.copy()                                           # 업데이트할 데이터 복사
        updated_data['item_name'] = 'Updated Item'                                       # 'item_name' 필드를 변경
        response = self.client.put(url, updated_data, format='json')                     # 배너 업데이트 요청 전송
        assert response.status_code == status.HTTP_200_OK                                # 응답 상태 코드가 200(OK)인지 확인
        assert response.data['data']['item_name'] == 'Updated Item'                      # 응답 데이터의 'item_name'이 업데이트된 값과 일치하는지 확인

    # 배너 삭제 테스트
    def test_delete_banner(self):
        url = reverse('handle_banner', args=[self.banner.id])  # 배너 삭제 엔드포인트 URL 생성
        response = self.client.delete(url)                              # 배너 삭제 요청 전송
        assert response.status_code == status.HTTP_200_OK               # 응답 상태 코드가 200(OK)인지 확인
        assert not Banner.objects.filter(id=self.banner.id).exists()    # 배너가 데이터베이스에서 삭제되었는지 확인

    # 존재하지 않는 배너 조회 테스트
    def test_get_nonexistent_banner(self):
        url = reverse('handle_banner', args=[9999])      # 존재하지 않는 배너 조회 엔드포인트 URL 생성
        response = self.client.get(url)                           # 배너 조회 요청 전송
        assert response.status_code == status.HTTP_404_NOT_FOUND  # 응답 상태 코드가 404(Not Found)인지 확인

    # 존재하지 않는 배너 업데이트 테스트
    def test_update_nonexistent_banner(self):
        url = reverse('handle_banner', args=[9999])              # 존재하지 않는 배너 업데이트 엔드포인트 URL 생성
        response = self.client.put(url, self.banner_data, format='json')  # 배너 업데이트 요청 전송
        assert response.status_code == status.HTTP_404_NOT_FOUND          # 응답 상태 코드가 404(Not Found)인지 확인

    # 존재하지 않는 배너 삭제 테스트
    def test_delete_nonexistent_banner(self):
        url = reverse('handle_banner', args=[9999])      # 존재하지 않는 배너 삭제 엔드포인트 URL 생성
        response = self.client.delete(url)                        # 배너 삭제 요청 전송
        assert response.status_code == status.HTTP_404_NOT_FOUND  # 응답 상태 코드가 404(Not Found)인지 확인