from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'profile_picture')

admin.site.register(UserProfile, UserProfileAdmin)
