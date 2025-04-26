# filepath: c:\Users\joelt\Development\notifier\notify-api\dummy_apis\serializers.py
from rest_framework import serializers

class DummyAPI1Serializer(serializers.Serializer):
    age = serializers.IntegerField(required=True, min_value=1, error_messages={
        "required": "The 'age' field is required.",
        "invalid": "The 'age' field must be a valid integer.",
        "min_value": "The 'age' field must be greater than 0."
    })

class DummyAPI2Serializer(serializers.Serializer):
    field_value = serializers.CharField(required=True, error_messages={
        "required": "The 'field_value' field is required.",
        "invalid": "The 'field_value' field must be a valid input."
    })

    def validate_field_value(self, value):
        # Check if the value is numeric
        if not value.isdigit():
            raise serializers.ValidationError("The 'field_value' field must be numeric.")
        return value