from django.urls import path
from .views import recreate_background_view, recreated_background_manage


urlpatterns = [
    path('api/v1/recreated-backgrounds', recreate_background_view, name='recreated-backgrounds'),
    path('api/v1/recreated-backgrounds/<int:recreated_background_id>', recreated_background_manage, name='recreated-background-manage')
]
