from django.db import models
from django.utils.timezone import now, timedelta


class NotificationRule(models.Model):
    """
    Model to define notification rules for APIs.
    """
    api_name = models.CharField(max_length=255, unique=True)
    notification_method = models.CharField(
        max_length=50,
        choices=[('email', 'Email'), ('sms', 'SMS'), ('both', 'Both')],
        default='both'
    )
    threshold = models.IntegerField(default=1)  # Max notifications allowed
    frequency = models.IntegerField(default=60)  # Time period in minutes

    def __str__(self):
        return f"{self.api_name} - {self.notification_method}"

    def is_within_threshold(self):
        """
        Check if the number of notifications sent within the frequency period
        is within the defined threshold.
        """
        recent_notifications = FailureLog.objects.filter(
            api_name=self.api_name,
            timestamp__gte=now() - timedelta(minutes=self.frequency)
        ).count()
        return recent_notifications < self.threshold


class FailureLog(models.Model):
    """
    Model to log API failures and notification details.
    """
    api_name = models.CharField(max_length=255, default='unknown')
    error_message = models.TextField()
    severity = models.CharField(
        max_length=50,
        choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('critical', 'Critical')],
        default='critical'
    )
    notification_method = models.CharField(
        max_length=50,
        choices=[('email', 'Email'), ('sms', 'SMS'), ('both', 'Both'), ('none', 'None')],
        default='none'
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.api_name} - {self.severity} - {self.timestamp}"