from rest_framework import serializers
from app.features.permission_role.models import (
    PermissionRole,
    FunctionRule,
)


class FunctionRuleSerializer(serializers.ModelSerializer):

    class Meta:
        model = FunctionRule
        fields = ['function_key']


class PermissionRoleSerializer(serializers.ModelSerializer):
    function_rules = FunctionRuleSerializer(read_only=True, many=True)

    class Meta:
        model = PermissionRole
        fields = [
            'code',
            'function_rules',
            ]