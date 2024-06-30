from django.db import models
from app.features.operator.querymanagers import OperatorQueryManager


class Operator(models.Model):
    name = models.CharField(max_length=200)

    objects = OperatorQueryManager()

    def __str__(self):
        return self.name