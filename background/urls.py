from django.urls import path
from .views import generate_background

urlpatterns = [
    path('generate/', generate_background, name='generate-background'),
]
