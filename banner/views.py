import logging
import httpx
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Banner, UserInteraction, Image
from .serializers import BannerSerializer, BannerDetailSerializer, BannerUpdateSerializer
import environ
from asgiref.sync import async_to_sync

# 환경 변수 로드
env = environ.Env()
environ.Env.read_env()

# OpenAI API 키 설정
openai_api_key = env("OPENAI_API_KEY")

# 로거 설정
logger = logging.getLogger(__name__)

# 광고 문구 생성을 위한 비동기 함수
async def generate_ad_text(item_name, item_concept, item_category, add_information, interaction_data):
    headers = {
        'Authorization': f'Bearer {openai_api_key}',  # OpenAI API 키를 헤더에 포함
        'Content-Type': 'application/json'
    }
    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system",
             "content": "당신은 창의적인 카피라이터입니다. 각 요청에 대해 일관된 광고 문구를 한 문장으로 생성하세요. 광고 문구는 최대 20자 이내의 완전한 문장으로 작성하세요. 글자 수 제한에 따라 완전한 문장이 되지 않는다면 다시 생성해주세요."},
            {"role": "user", "content": f"다음 정보를 바탕으로 '{item_name}' 제품의 광고 문구를 1문장만 생성해 주세요: "
                                        f"컨셉 - '{item_concept}', 카테고리 - '{item_category}', 추가 정보 - '{add_information}'. "
                                        f"이전에 결과값과의 상호작용: {interaction_data}"}
        ],
        "max_tokens": 50  # 최대 토큰 수를 50으로 설정
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
            response.raise_for_status()
            response_json = response.json()
            maintext = response_json['choices'][0]['message']['content'].strip().strip('\"')
            return maintext[:20]  # 광고 문구를 최대 20자 이내로 제한
        except httpx.HTTPStatusError as exc:
            logger.error(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
            raise

async def generate_serve_text(maintext, item_concept, item_category, add_information, interaction_data):
    headers = {
        'Authorization': f'Bearer {openai_api_key}',  # OpenAI API 키를 헤더에 포함
        'Content-Type': 'application/json'
    }
    data = {
        "model": "gpt-4",
        "messages": [
            {"role": "system",
             "content": "당신은 창의적인 카피라이터입니다. 각 요청에 대해 일관된 광고 문구를 생성하세요. 광고 문구는 최대 20자 이내의 완전한 문장으로 작성하세요. 글자 수 제한에 따라 완전한 문장이 되지 않는다면, 다시 생성해주세요."},
            {"role": "user",
             "content": f"다음 정보를 바탕으로 광고글의 내용을 뒷받침하는 서브 광고글을 작성해 주세요: '{maintext}'. '{maintext}' 와는 다른 문장으로 작성하세요. "
                        f"컨셉 - '{item_concept}', 카테고리 - '{item_category}', 추가 정보 - '{add_information}'. "
                        f"이전에 결과값과의 상호작용: {interaction_data}"}
        ],
        "max_tokens": 50  # 최대 토큰 수를 50으로 설정
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
            response.raise_for_status()
            response_json = response.json()
            servetext = response_json['choices'][0]['message']['content'].strip().strip('\"')
            return servetext[:30]  # 서브 광고 문구를 최대 30자 이내로 제한
        except httpx.HTTPStatusError as exc:
            logger.error(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}.")
            raise

# 광고 문구와 서브 광고 문구를 생성하는 비동기 함수
async def generate_ad_and_serve_texts(item_name, item_concept, item_category, add_information, interaction_data):
    maintext = await generate_ad_text(item_name, item_concept, item_category, add_information, interaction_data)
    servetext = await generate_serve_text(maintext, item_concept, item_category, add_information, interaction_data)
    maintext2 = await generate_ad_text(item_name, item_concept, item_category, add_information, interaction_data)
    servetext2 = await generate_serve_text(maintext2, item_concept, item_category, add_information, interaction_data)
    return maintext, servetext, maintext2, servetext2

# Swagger를 이용한 API 문서화와 배너 생성 API
@swagger_auto_schema(
    method='post',
    operation_id='배너 생성',
    operation_description='광고 배너를 생성합니다. item_name, item_concept, item_category를 입력해야 합니다.',
    request_body=BannerSerializer,
    responses={
        201: openapi.Response(
            description='배너 생성 성공',
            schema=BannerDetailSerializer,
            examples={
                'application/json': {
                    "code": 201,
                    "message": "배너 생성 성공",
                    "data": {
                        "id": 1,
                        "item_name": "에어팟 프로2",
                        "item_concept": "중국산",
                        "item_category": "전자제품",
                        "maintext": "에어팟 프로2를 소개합니다! 이제 중국산 품질로 만나보세요.",
                        "servetext": "에어팟 프로2 광고를 확인해 보세요!",
                        "maintext2": "편안한 착용감으로 중국산 전자기기의",
                        "servetext2": "중국산 전자기기의 새로운 선택, 탁월한 가성비!",
                        "created_at": "2023-01-01T00:00:00Z"
                    }
                }
            }
        ),
        400: '잘못된 요청',
    }
)
@api_view(['POST'])
def create_banner(request):
    serializer = BannerSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data

        item_name = data['item_name']
        item_concept = data['item_concept']
        item_category = data['item_category']
        add_information = data['add_information']
        image_instance = data['image_id']
        user_instance = data['user_id']

        # 이전 상호작용 기록 가져오기
        interaction_records = UserInteraction.objects.filter(image_id=image_instance).order_by('-created_at')
        interaction_data = " ".join(record.interaction_data for record in interaction_records)

        # 비동기 태스크로 광고 문구 생성
        maintext, servetext, maintext2, servetext2 = async_to_sync(generate_ad_and_serve_texts)(
            item_name, item_concept, item_category, add_information, interaction_data
        )

        # Banner 객체 생성 및 저장
        banner = Banner.objects.create(
            item_name=item_name,
            item_concept=item_concept,
            item_category=item_category,
            maintext=maintext,
            servetext=servetext,
            maintext2=maintext2,
            servetext2=servetext2,
            user_id=user_instance,
            image_id=image_instance,
            add_information=add_information,
        )

        response_data = {
            "code": 201,
            "message": "배너 생성 성공",
            "data": BannerDetailSerializer(banner).data,
        }

        return Response(response_data, status=status.HTTP_201_CREATED)

    return Response({"code": 400, "message": "배너 생성 실패", "errors": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST)

# 배너 조회, 수정, 삭제 API를 위한 Swagger 설정
@swagger_auto_schema(
    method='get',
    operation_id='배너 조회',
    operation_description='ID를 통해 광고 배너를 조회합니다.',
    responses={
        200: openapi.Response(
            description='배너 조회 성공',
            examples={
                'application/json': {
                    "code": 200,
                    "message": "배너 조회 성공",
                    "data": {
                        "id": 1,
                        "maintext": "훌륭한 중국산 전자기기, 에어팟으로",
                        "servetext": "프리미엄 다소 강조헤 중국산 전자기기, 지금 확인하세",
                        "maintext2": "편안한 착용감으로 중국산 전자기기의",
                        "servetext2": "중국산 전자기기의 새로운 선택, 탁월한 가성비!"
                    }
                }
            }
        ),
        404: '배너 조회 실패',
    }
)
@swagger_auto_schema(
    method='put',
    operation_id='배너 수정',
    operation_description='ID를 통해 광고 배너를 수정합니다. item_name, item_concept, item_category를 입력해야 합니다.',
    request_body=BannerUpdateSerializer,
    responses={
        200: '배너 수정 성공',
        404: '배너 수정 실패',
    }
)
@swagger_auto_schema(
    method='delete',
    operation_id='배너 삭제',
    operation_description='ID를 통해 광고 배너를 삭제합니다.',
    responses={
        200: '배너 삭제 성공',
        404: '배너 삭제 실패',
    }
)
@api_view(['GET', 'PUT', 'DELETE'])
def handle_banner(request, bannerId):
    try:
        banner = Banner.objects.get(id=bannerId)  # 배너 ID로 배너 객체를 조회
    except Banner.DoesNotExist:
        return Response({"code": 404, "message": "배너 조회 실패"}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        # 원하는 필드만 포함한 데이터 생성
        data = {
            "id": banner.id,
            "maintext": banner.maintext,
            "servetext": banner.servetext,
            "maintext2": banner.maintext2,
            "servetext2": banner.servetext2,
        }
        return Response({"code": 200, "message": "배너 조회 성공", "data": data}, status=status.HTTP_200_OK)

    elif request.method == 'PUT':
        serializer = BannerUpdateSerializer(banner, data=request.data)
        if serializer.is_valid():
            item_name = serializer.validated_data.get('item_name')
            item_concept = serializer.validated_data.get('item_concept')
            item_category = serializer.validated_data.get('item_category')
            user_instance = serializer.validated_data.get('user_id')
            image_instance = serializer.validated_data.get('image_id')
            add_information = serializer.validated_data.get('add_information')

            # 이전 상호작용 기록 가져오기
            interaction_records = UserInteraction.objects.filter(image_id=image_instance).order_by('-created_at')
            interaction_data = " ".join(record.interaction_data for record in interaction_records)

            # 광고 문구와 서브 광고 문구 생성
            maintext, servetext, maintext2, servetext2 = async_to_sync(generate_ad_and_serve_texts)(
                item_name, item_concept, item_category, add_information, interaction_data
            )

            # 배너 객체 업데이트
            banner.item_name = item_name
            banner.item_concept = item_concept
            banner.item_category = item_category
            banner.maintext = maintext
            banner.servetext = servetext
            banner.maintext2 = maintext2
            banner.servetext2 = servetext2
            banner.user_id = user_instance
            banner.image_id = image_instance
            banner.add_information = add_information
            banner.save()

            # 새로운 상호작용 기록 저장
            UserInteraction.objects.create(image_id=image_instance,
                                           interaction_data=f"Updated banner with ad_text: {maintext}")

            response_data = {
                "code": 200,
                "message": "배너 수정 성공",
                "data": BannerDetailSerializer(banner).data,
            }

            return Response(response_data, status=status.HTTP_200_OK)

        return Response({"code": 400, "message": "배너 수정 실패", "errors": serializer.errors},
                        status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        banner.delete()  # 배너 객체 삭제
        return Response({"code": 200, "message": "배너 삭제 성공"}, status=status.HTTP_200_OK)

    return Response({"code": 405, "message": "Method not allowed"}, status=status.HTTP_405_METHOD_NOT_ALLOWED)