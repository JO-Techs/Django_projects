from django.db import models

class StatusCode(models.Model):
    """
    Defines the status codes used in the application
    """
    code = models.CharField(max_length=10, unique=True, help_text="Status code (e.g., '007')")
    name = models.CharField(max_length=100, help_text="Short name for this status code")
    description = models.TextField(help_text="Detailed description of what this status code means")
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class AadharVerification(models.Model):
    """
    Model for Aadhar verification requests
    """
    aadhar_number = models.CharField(max_length=12, help_text="12-digit Aadhar number")
    request_id = models.CharField(max_length=50, unique=True, help_text="Unique request identifier")
    status_code = models.ForeignKey(StatusCode, on_delete=models.CASCADE, help_text="Current status of verification")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Verification for {self.aadhar_number[-4:]} - {self.status_code}"