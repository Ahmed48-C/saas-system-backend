from django.urls import path
from app.features.userprofile.views import (
    get_all_userprofile,
    create_userprofile,
    get_userprofile_by_id,
    update_userprofile,
    delete_userprofile,
)

urlpatterns = [
    path('get/userprofile/<userprofile_id>/', get_userprofile_by_id),
    path('get/userprofiles/', get_all_userprofile),
    path('post/userprofile/', create_userprofile),
    path('put/userprofile/<userprofile_id>/', update_userprofile),
    path('delete/userprofile/<userprofile_id>/', delete_userprofile),
]