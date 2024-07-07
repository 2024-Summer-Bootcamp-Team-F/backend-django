from django.urls import path

from user import views
from user.views import get_nickname

app_name = 'user'

urlpatterns = [
    path('', views.create_nickname, name='create-nickname'),
    path('<int:user_id>', get_nickname, name='get-nickname'),
]