from django.db import models

class FailureLog(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField()
    severity = models.CharField(max_length=50)
    notification_method = models.CharField(max_length=50, default='unknown')

    def __str__(self):
        return f"{self.timestamp} - {self.severity}: {self.error_message}"
    
class NotificationRule(models.Model):
    api_name = models.CharField(max_length=255, unique=True)  # Name of the API
    notification_method = models.CharField(
        max_length=50,
        choices=[('email', 'Email'), ('sms', 'SMS'), ('both', 'Both')],
        default='both'
    )
    threshold = models.IntegerField(default=1)  # Max notifications allowed in the time period
    frequency = models.IntegerField(default=60)  # Time period in minutes

    def __str__(self):
        return f"{self.api_name} - {self.notification_method} - Max {self.threshold} notifications every {self.frequency} minutes"
    