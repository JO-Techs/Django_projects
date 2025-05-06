from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import (
    AadharValidator, 
    StatusCodeService, 
    VerificationService, 
    VerificationOutcomeSimulator
)
from deview.services import CustomerJourneyService

def api_test_view(request):
    """
    View for testing the API
    """
    return render(request, 'sampleapi/api_test.html')

class AadharVerifyAPI(APIView):
    """
    API endpoint for Aadhar verification
    """
    def post(self, request):
        # Extract data from request
        aadhar_number = request.data.get('aadhar_number')
        
        # Validate Aadhar number using the validator service
        is_valid, error_message = AadharValidator.validate(aadhar_number)
        if not is_valid:
            # Record this as a validation failure
            CustomerJourneyService.record_status('aadhar_validation', '001', 'Invalid Aadhar Number')
            return Response({
                'status': 'error',
                'message': error_message,
                'code': '001'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Simulate verification outcome
        outcome, status_code_value, http_status, name, description = VerificationOutcomeSimulator.simulate()
        
        # Get or create the status code
        status_code = StatusCodeService.get_or_create(
            status_code_value,
            name=name,
            description=description
        )
        
        # Create verification record
        verification = VerificationService.create_verification(aadhar_number, status_code)
        
        # Record this in customer journey
        CustomerJourneyService.record_status('aadhar_verification', status_code_value, status_code.name)
        
        # Get response data based on outcome
        response_data = VerificationOutcomeSimulator.get_response_for_outcome(
            outcome, 
            verification.request_id, 
            status_code_value
        )
        
        # Return response with appropriate HTTP status
        return Response(response_data, status=http_status)

class VerificationStatusAPI(APIView):
    """
    API endpoint to check status of a verification request
    """
    def get(self, request, request_id):
        # Get verification using the service
        verification = VerificationService.get_verification(request_id)
        
        if verification:
            # Record this status check
            CustomerJourneyService.record_status(
                'check_verification_status', 
                verification.status_code.code, 
                'Status Check'
            )
            
            return Response({
                'status': 'success',
                'aadhar_number': verification.aadhar_number[-4:],  # Only show last 4 digits
                'status_code': verification.status_code.code,
                'status_name': verification.status_code.name,
                'status_description': verification.status_code.description,
                'created_at': verification.created_at,
                'updated_at': verification.updated_at
            })
        else:
            # Record this as a not found error
            CustomerJourneyService.record_status('check_verification_status', '404', 'Request Not Found')
            
            return Response({
                'status': 'error',
                'message': 'Verification request not found',
                'code': '404'
            }, status=status.HTTP_404_NOT_FOUND)