from django.contrib import admin

# Register your models here.
from app.features.userprofile.models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'location')
    search_fields = ('user__username', 'location__name')  # Adjust field names as necessary
