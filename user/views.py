from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from user.models import User
from user.serializers import NicknameCreateSerializer

import logging # 로그 검사
logger = logging.getLogger(__name__)

@swagger_auto_schema(
    method='post',
    operation_id='닉네임 생성',
    operation_description='닉네임을 이용해 유저를 생성합니다.\n\n닉네임은 중복이 허용되지 않습니다.',
    tags=['Users'],
    request_body=NicknameCreateSerializer,
    responses={
        201: "User successfully created.",
        400: "Bad request. Make sure to provide a valid nickname.",
    }
)
@api_view(['POST'])
def create_nickname(request, *args, **kwargs):
    """
    사용자 생성
    """
    nickname = request.data.get("nickname")
    logger.debug("nickname: ",nickname)
    # 내용 없는 경우
    if not nickname:
        return Response({"error": "닉네임을 작성해주세요."}, status=status.HTTP_400_BAD_REQUEST)

    # 닉네임 중복 및 공백 검사 수행
    serializer = NicknameCreateSerializer(data=request.data)
    try:
        serializer.is_valid(raise_exception=True)
    except serializers.ValidationError as e:
        logger.error("e: ", e)
        error_message = {
            "error": e.detail["nickname"][0],
            "error_code": e.get_codes()["nickname"][0]
        }
        return Response(error_message, status=status.HTTP_400_BAD_REQUEST)

    # 문제 없으면 저장
    user = User.objects.create(nickname=nickname)
    return Response({"success": "사용자가 성공적으로 생성되었습니다.", "data": {"id": user.id, "nickname" : nickname}}, status=status.HTTP_201_CREATED)


@swagger_auto_schema(
    method='get',
    operation_id='닉네임 조회',
    operation_description='닉네임을 조회합니다',
    tags=['Users'],
)
@api_view(['GET'])
def get_nickname(request, user_id):
    user_nickname = User.objects.get(id=user_id).nickname
    return Response({"success": "사용자가 성공적으로 조회되었습니다.", "data": { "nickname": user_nickname}},
                    status=status.HTTP_201_CREATED)