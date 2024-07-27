from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls.static import static
from django.conf import settings

# API 스키마를 만들기 위한 뷰를 생성하는 데 사용, Swagger UI와 연동되어 API 문서를 제공하고 시각적으로 보여줌
schema_view = get_schema_view(
    openapi.Info(
        title="TakerPicture API",               # API의 제목을 설정
        default_version='v1',                   # API의 기본 버전을 설정
        description="Teamf API 문서",            # API에 대한 설명을 설정
    ),
    public=True,                                # API 스키마가 공개되도록 설정
    permission_classes=[permissions.AllowAny],  # 누구나 API 스키마를 조회할 수 있도록 허용
    #url='https://techeerpicture.store/api/v1'
)

# URL 패턴 목록
urlpatterns = [
    path('admin/', admin.site.urls),                                                # 관리자 사이트 URL
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),  # Swagger UI를 제공하는 URL
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),          # Redoc UI를 제공하는 URL
    path('api/v1/nicknames/', include('user.urls')),                                # 'user' 앱의 URL을 포함
    path('api/v1/banners/', include('banner.urls')),                                # 'banner' 앱의 URL을 포함
    path('api/v1/', include('image.urls')),                                         # 'image' 앱의 URL을 포함
    path('api/v1/', include('background.urls')),                                    # 'background' 앱의 URL을 포함
    path('api/v1/', include('recreated_background.urls')),                          # 'recreated_background' 앱의 URL을 포함
    path('api/v1/', include('image_resizing.urls')),
                               # 'image_resizing' 앱의 URL을 포함
    path('', include('django_prometheus.urls')),                                    # 'django_prometheus' 앱의 URL을 포함
    path('api/v1/texttovideo/', include('texttovideo.urls')),
]

# Swagger JSON 형식 스키마와 UI를 위한 URL 패턴 추가
urlpatterns += [
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"  # Swagger JSON 형식 스키마 URL
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",  # Swagger UI URL
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),  # Redoc UI URL
]

# Static 파일을 서빙하기 위한 URL 패턴 추가
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)