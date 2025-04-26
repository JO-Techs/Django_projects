from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from notify.apps.notifications.logs import create_failure_log
from notify.apps.notifications.models import NotificationRule
from notify.apps.notifications.threshold import handle_threshold_logic
from .serializers import DummyAPI1Serializer, DummyAPI2Serializer


# filepath: c:\Users\joelt\Development\notifier\notify-api\dummy_apis\views.py
from django.shortcuts import render

class DummyAPI1(APIView):
    def get(self, request):
        return render(request, 'dummy_api1_age_validation.html')

    def post(self, request):
        serializer = DummyAPI1Serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        age = serializer.validated_data.get('age')
        if age < 18:
            failure_details = f"Age validation failed. Provided age: {age}."
            data = {
                'api_name': 'Dummy API 1',
                'failure_details': failure_details,
                'notification_method': 'both'
            }

            # Handle threshold logic
            if not handle_threshold_logic(data, serializer):
                return Response(
                    {"error": "Notification suppressed due to threshold."},
                    status=status.HTTP_200_OK
                )

            return Response(
                {"message": "Failure logged and notification sent."},
                status=status.HTTP_201_CREATED
            )

        return Response({"message": "Age is valid."}, status=status.HTTP_200_OK)
# filepath: c:\Users\joelt\Development\notifier\notify-api\dummy_apis\views.py
from django.shortcuts import render

class DummyAPI2(APIView):
    def get(self, request):
        return render(request, 'dummy_api2_data_validation.html')

    def post(self, request):
        serializer = DummyAPI2Serializer(data=request.data)
        if not serializer.is_valid():
            # Log the failure for invalid input
            create_failure_log(
                api_name='Dummy API 2',
                error_message=f"Invalid input received: {request.data.get('field_value')}. Error: {serializer.errors.get('field_value')}",
                severity='critical',
                notification_method='none'
            )
            return Response({
                'error': serializer.errors.get('field_value', ['An error occurred'])[0]
            }, status=status.HTTP_400_BAD_REQUEST)

        # If the input is valid, return a success response
        return Response({"message": "Field value is valid."}, status=status.HTTP_200_OK)