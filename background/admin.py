from django.contrib import admin
from background.models import (Background)
class BackgroundAdmin(admin.ModelAdmin):
    search_fields = ['gen_type', 'concept_option', 'image_url']

admin.site.register(Background, BackgroundAdmin)