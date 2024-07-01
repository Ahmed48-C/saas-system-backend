from django.contrib import admin

# Register your models here.
from app.features.permission_role.models import (
    PermissionRole,
    PermissionRoleFunctionRule,
    FunctionRule,
)


@admin.register(FunctionRule)
class FunctionRuleAdmin(admin.ModelAdmin):

    list_display = [
        'function_key',
    ]


class FunctionRuleInline(admin.TabularInline):
    model = PermissionRoleFunctionRule
    extra = 0
    fields = ('function_rule',)
    raw_id_fields = ('function_rule',)


@admin.register(PermissionRole)
class PermissionRoleAdmin(admin.ModelAdmin):

    list_display = [
        'code',
        'description',
    ]

    inlines = (FunctionRuleInline,)

