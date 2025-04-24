from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils.email_sender import send_failure_notification
from .utils.sms_sender import MockSMSService
from .models import FailureLog, NotificationRule
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now, timedelta

#FOR LOGGING
import logging
logger = logging.getLogger(__name__)

def frontend_view(request):
    return render(request, 'index.html')  

def failure_logs_view(request):
    # Fetch all failure logs
    logs = FailureLog.objects.all().order_by('-timestamp')  # ORDER Latest first
    return render(request, 'failure_logs.html', {'logs': logs})

def manage_rules_view(request):
    if request.method == 'POST':
        if 'delete_rule' in request.POST:
            # Delete the rule
            rule_id = request.POST.get('rule_id')
            rule = get_object_or_404(NotificationRule, id=rule_id)
            rule.delete()
            return redirect('manage-rules')

        # Create or update the rule
        api_name = request.POST.get('api_name')
        notification_method = request.POST.get('notification_method')
        threshold = request.POST.get('threshold', 1)
        frequency = request.POST.get('frequency', 60)

        rule, created = NotificationRule.objects.update_or_create(
            api_name=api_name,
            defaults={
                'notification_method': notification_method,
                'threshold': threshold,
                'frequency': frequency,
            }
        )
        return redirect('manage-rules')

    rules = NotificationRule.objects.all()
    return render(request, 'manage_rules.html', {'rules': rules})

class FailureNotificationView(APIView):
    def post(self, request):
        api_name = request.data.get('api_name', None)
        failure_details = request.data.get('failure_details', None)
        notification_method = request.data.get('notification_method', None)

        if not api_name or not failure_details:
            logger.error("API name or failure details missing in the request.")
            return Response({"error": "API name and failure details are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            rule = NotificationRule.objects.get(api_name=api_name)
            logger.info(f"NotificationRule found for {api_name}: {rule.notification_method}, Threshold: {rule.threshold}, Frequency: {rule.frequency}")
        except NotificationRule.DoesNotExist:
            logger.error(f"No NotificationRule found for {api_name}.")
            return Response({"error": f"No notification rule found for API: {api_name}"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the number of notifications sent for this API in the last `frequency` minutes exceeds the threshold
        recent_notifications = FailureLog.objects.filter(
            timestamp__gte=now() - timedelta(minutes=rule.frequency),
            severity="critical",
            api_name=api_name  # Ensure filtering by API name
        ).count()
        logger.info(f"Recent notifications for {api_name}: {recent_notifications}, Threshold: {rule.threshold}")

        if recent_notifications >= rule.threshold:
            # Check if a similar failure has already been logged recently for this API
            existing_log = FailureLog.objects.filter(
                api_name=api_name,
                error_message=failure_details,
                timestamp__gte=now() - timedelta(minutes=rule.frequency),
                notification_method="none"
            ).exists()

            if not existing_log:
                FailureLog.objects.create(
                    api_name=api_name,
                    error_message=failure_details,
                    severity="critical",
                    notification_method="none"
                )
            logger.warning(f"Notification suppressed for {api_name} due to threshold.")
            return Response({"error": "Max notification limit reached for this API. Notification suppressed."}, status=status.HTTP_200_OK)

        # Use the notification method from the request if provided, otherwise fallback to the rule's method
        if not notification_method:
            notification_method = rule.notification_method

        logger.info(f"Notification method for {api_name}: {notification_method}")

        # Send notifications based on the notification method
        if notification_method in ['email', 'both']:
            logger.info(f"Sending email notification for {api_name}.")
            send_failure_notification(f"API: {api_name}, Details: {failure_details}")

        if notification_method in ['sms', 'both']:
            logger.info(f"Sending SMS notification for {api_name}.")
            sms_service = MockSMSService(from_number="mock_sender_number")
            sms_service.send_sms("mock_recipient_number", f"API: {api_name}, Details: {failure_details}")

        # Save the failure log
        FailureLog.objects.create(
            api_name=api_name,
            error_message=failure_details,
            severity="critical",
            notification_method=notification_method
        )
        logger.info(f"Failure log created for {api_name} with notification method: {notification_method}")

        return Response({"message": "Notification sent successfully."}, status=status.HTTP_200_OK)
