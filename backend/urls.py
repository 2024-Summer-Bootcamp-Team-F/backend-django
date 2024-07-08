from django.contrib import admin
from django.urls import path, include
#users 에서 쓸 앤드포인트가 들어가
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf.urls.static import static
from django.conf import settings



schema_view = get_schema_view(                  #  API 스키마를 만들기 위한 뷰를 생성하는 데 사용,Swagger UI와 연동되어 API 문서를 제공하고 시각적으로 보여줌
    openapi.Info(                               #  API의 기본 정보를 설정
        title="TakerPicture API",
        default_version='v1',
        description="Teamf API 문서",
    ),
    public=True,                                #  API 스키마가 공개되도록 설정
    permission_classes=[permissions.AllowAny],  #  누구나 API 스키마를 조회할 수 있도록 허용
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Add more URL patterns here as needed
    path('api/v1/nicknames/', include('user.urls')),
    path('api/v1/', include('image.urls')),
]

urlpatterns += [
    path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
