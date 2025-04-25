from rest_framework import serializers
from .models import FailureLog, NotificationRule

class FailureLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = FailureLog
        fields = '__all__'

class NotificationRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationRule
        fields = '__all__'

class DummyAPI1Serializer(serializers.Serializer):
    age = serializers.IntegerField(required=True, min_value=1, error_messages={
        "required": "The 'age' field is required.",
        "invalid": "The 'age' field must be a valid integer.",
        "min_value": "The 'age' field must be greater than 0."
    })

class DummyAPI2Serializer(serializers.Serializer):
    field_value = serializers.IntegerField(required=True, error_messages={
        "required": "The 'field_value' field is required.",
        "invalid": "The 'field_value' field must be a valid integer."
    })