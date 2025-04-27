# serializers.py
from rest_framework import serializers

class DataSerializer(serializers.Serializer):
    field_value = serializers.CharField()


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta

from .serializers import DataSerializer
from .models import FailureLog

class DummyAPI2View(APIView):
    def post(self, request, format=None):
        serializer = DataSerializer(data=request.data)
        if serializer.is_valid():
            value = serializer.validated_data['field_value']
            # Try to parse as a number
            try:
                numeric_value = float(value)
                # If parsing succeeds, treat as valid input
                return Response({"message": "Data is valid."}, status=status.HTTP_200_OK)
            except ValueError:
                # Non-numeric input: log failure and handle notification
                details = f"Invalid input received: {value}. Error: \"The 'field_value' field must be numeric.\"
                # Threshold and Notification Logic 
                # Example: allow up to 3 notifications per hour (same as Dummy API 1)
                one_hour_ago = timezone.now() - timedelta(hours=1)
                recent_notifs = FailureLog.objects.filter(
                    timestamp__gte=one_hour_ago,
                    notification_method='Both'
                ).count()
                if recent_notifs < 3:
                    # Send notification (email/SMS) – implement as in Dummy API 1
                    # (Placeholder code – replace with real email/SMS logic)
                    # send_email("Alert: Data validation failure", details)
                    # send_sms(f"Alert: {details}")
                    notification_method = 'Both'
                    severity = 'high'
                else:
                    # Suppress additional notifications
                    notification_method = 'None'
                    severity = 'critical'
                    details = f"Notification suppressed due to threshold. Details: {details}"
                # Log the failure
                FailureLog.objects.create(
                    details=details,
                    severity=severity,
                    notification_method=notification_method
                )
                # Return the success-style message
                return Response(
                    {"message": "Failure logged and notification sent."},
                    status=status.HTTP_200_OK
                )
        else:
            # (Optional) Handle missing or malformed field cases
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


// Assuming your HTML has:
// <input id="field-value-input" ...>
// <button id="validate-data-btn">Validate Data</button>
// <div id="result-message"></div>

document.getElementById("validate-data-btn").addEventListener("click", function() {
  const input = document.getElementById("field-value-input").value;
  fetch("/dummy-apis/dummy-api-2/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ field_value: input })
  })
  .then(response => response.json())
  .then(data => {
    const resultEl = document.getElementById("result-message");
    // Remove any error styling, apply success styling
    resultEl.classList.remove("error-message");
    resultEl.classList.add("success-message");
    // Display the message from the server
    resultEl.textContent = data.message;
  })
  .catch(error => {
    console.error("Unexpected error:", error);
  });
});

