from django.contrib import admin

from user.models import User


# Register your models here.
class UserAdmin(admin.ModelAdmin):
    search_fields = ['nickname']

admin.site.register(User, UserAdmin)