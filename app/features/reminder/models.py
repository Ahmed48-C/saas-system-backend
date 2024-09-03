from django.db import models
from app.features.reminder.querymanagers import ReminderQueryManager
from app.features.operator.models import Operator
# Create your models here.

class Reminder(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateField()
    time = models.TimeField()
    reached = models.BooleanField(default=False)

    operator = models.ForeignKey(Operator, on_delete=models.PROTECT, null=True, blank=True)

    objects = ReminderQueryManager()

    def __str__(self):
        return self.name