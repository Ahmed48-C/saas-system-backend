from django.db import models
from app.features.permission_role.querymanagers import PermissionRoleQueryManager


class FunctionRule(models.Model):
    function_key = models.CharField(max_length=80)

    # for CRUD permissions
    # can_read = models.BooleanField(default=False)
    # can_create = models.BooleanField(default=False)
    # can_update = models.BooleanField(default=False)
    # can_delete = models.BooleanField(default=False)

    def __str__(self):
        return self.function_key

class PermissionRole(models.Model):
    code = models.CharField(max_length=200)
    description = models.CharField(max_length=255, null=True, blank=True)

    function_rules = models.ManyToManyField(
        FunctionRule,
        verbose_name='function rule',
        through='PermissionRoleFunctionRule'
    )

    objects = PermissionRoleQueryManager()

    def __str__(self):
        return self.code

class PermissionRoleFunctionRule(models.Model):
    permission_role = models.ForeignKey(PermissionRole, on_delete=models.CASCADE)
    function_rule = models.ForeignKey(FunctionRule, on_delete=models.CASCADE)