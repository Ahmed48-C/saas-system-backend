from django.contrib.auth.models import User
from django.db import models
from app.features.operator.models import Operator
from app.features.location.models import Location
from app.features.userprofile.querymanagers import UserProfileQueryManager


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    location = models.ForeignKey(Location, on_delete=models.PROTECT, null=True, blank=True)
    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True, blank=True)
    objects = UserProfileQueryManager()

    def __str__(self):
        return self.user.username