from rest_framework import serializers
from .models import BackgroundImage

class BackgroundImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BackgroundImage
        fields = [
            'id', 'user', 'image', 'gen_type', 'concept_option', 'output_h',
            'output_w', 'image_url', 'created_at', 'updated_at', 'is_deleted', 'recreated'
        ]
        read_only_fields = ['id', 'image_url', 'created_at', 'updated_at']
