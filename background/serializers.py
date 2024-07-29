from rest_framework import serializers
from .models import Background
class BackgroundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Background
        fields = [
            'id', 'user', 'image_url', 'output_h', 'output_w'
        ]
        read_only_fields = ['id', 'image_url']
