from django.shortcuts import render
from rest_framework.generics import CreateAPIView
from notify.apps.notifications.models import FailureLog
from notify.apps.notifications.serializers import DummyAPI1Serializer, DummyAPI2Serializer
from rest_framework import serializers

def dummy_api1_age_validation_view(request):
    return render(request, 'dummy_api1_age_validation.html')

def dummy_api2_data_validation_view(request):
    return render(request, 'dummy_api2_data_validation.html')

from rest_framework.response import Response
from rest_framework import status

class DummyAPI1(CreateAPIView):
    queryset = FailureLog.objects.all()
    serializer_class = DummyAPI1Serializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        age = serializer.validated_data.get('age')
        if age < 18:
            failure_details = f"Age validation failed. Provided age: {age} (must be 18 or older)."
            FailureLog.objects.create(
                api_name="Dummy API 1",
                error_message=failure_details,
                severity="critical",
                notification_method="none"
            )
            return Response({"message": "Failure logged for age validation."}, status=status.HTTP_201_CREATED)

        return Response({"message": "Age is valid."}, status=status.HTTP_200_OK)
    
class DummyAPI2(CreateAPIView):
    queryset = FailureLog.objects.all()
    serializer_class = DummyAPI2Serializer

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            field_value = serializer.validated_data.get('field_value')
            failure_details = f"Dummy API 2 failed due to invalid data format for 'field_value': {field_value}."

            # Create a failure log
            FailureLog.objects.create(
                api_name="Dummy API 2",
                error_message=failure_details,
                severity="critical",
                notification_method="none"
            )

            return Response({"message": "Failure logged for data validation."}, status=status.HTTP_201_CREATED)
        except serializers.ValidationError as e:
            # Return user-friendly error messages
            return Response({"error": e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Log unexpected errors
            logger.error(f"Unexpected error in DummyAPI2: {str(e)}")
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)