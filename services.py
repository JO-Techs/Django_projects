"""
Services for the SampleAPI app.
This file implements the service layer following the SOLID principles.
"""
import uuid
import random
from django.core.cache import cache
from .models import AadharVerification, StatusCode

class AadharValidator:
    """
    Responsible for validating Aadhar numbers (Single Responsibility Principle)
    """
    @staticmethod
    def validate(aadhar_number):
        """
        Validate an Aadhar number
        Returns (is_valid, error_message)
        """
        if not aadhar_number:
            return False, "Aadhar number is required"
        
        if len(aadhar_number) != 12:
            return False, "Aadhar number must be 12 digits"
        
        if not aadhar_number.isdigit():
            return False, "Aadhar number must contain only digits"
        
        return True, None


class StatusCodeService:
    """
    Handles operations related to status codes (Single Responsibility Principle)
    """
    CACHE_PREFIX = "status_code_"
    CACHE_TIMEOUT = 3600  # 1 hour
    
    @classmethod
    def get_or_create(cls, code, name=None, description=None):
        """
        Get a status code from cache or database, create if it doesn't exist
        """
        # Try to get from cache first
        cache_key = f"{cls.CACHE_PREFIX}{code}"
        status_code = cache.get(cache_key)
        
        if status_code is None:
            # Not in cache, try to get from database
            try:
                status_code = StatusCode.objects.get(code=code)
            except StatusCode.DoesNotExist:
                # Create new status code
                if name and description:
                    status_code = StatusCode.objects.create(
                        code=code,
                        name=name,
                        description=description
                    )
                else:
                    # If no name/description provided, we can't create it
                    return None
            
            # Store in cache for future use
            cache.set(cache_key, status_code, cls.CACHE_TIMEOUT)
        
        return status_code


class VerificationService:
    """
    Handles verification operations (Single Responsibility Principle)
    """
    CACHE_PREFIX = "verification_"
    CACHE_TIMEOUT = 1800  # 30 minutes
    
    @classmethod
    def create_verification(cls, aadhar_number, status_code):
        """
        Create a new verification record
        """
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        
        # Create verification record
        verification = AadharVerification.objects.create(
            aadhar_number=aadhar_number,
            request_id=request_id,
            status_code=status_code
        )
        
        # Cache the verification for faster retrieval
        cache_key = f"{cls.CACHE_PREFIX}{request_id}"
        cache.set(cache_key, verification, cls.CACHE_TIMEOUT)
        
        return verification
    
    @classmethod
    def get_verification(cls, request_id):
        """
        Get a verification by request ID, using cache if available
        """
        # Try to get from cache first
        cache_key = f"{cls.CACHE_PREFIX}{request_id}"
        verification = cache.get(cache_key)
        
        if verification is None:
            # Not in cache, try to get from database
            try:
                verification = AadharVerification.objects.get(request_id=request_id)
                # Store in cache for future use
                cache.set(cache_key, verification, cls.CACHE_TIMEOUT)
            except AadharVerification.DoesNotExist:
                return None
        
        return verification


class VerificationOutcomeSimulator:
    """
    Simulates verification outcomes (Open/Closed Principle - can be extended with new outcomes)
    """
    # Outcome definitions with weights and status codes
    OUTCOMES = {
        'success': {'weight': 70, 'code': '200', 'http_status': 200},
        'pending': {'weight': 10, 'code': '100', 'http_status': 200},
        'not_found': {'weight': 10, 'code': '404', 'http_status': 404},
        'server_error': {'weight': 5, 'code': '500', 'http_status': 500},
        'timeout': {'weight': 5, 'code': '504', 'http_status': 504}
    }
    
    @classmethod
    def simulate(cls):
        """
        Simulate a verification outcome
        Returns (outcome_name, status_code, http_status)
        """
        # Extract outcomes and weights
        outcomes = list(cls.OUTCOMES.keys())
        weights = [cls.OUTCOMES[o]['weight'] for o in outcomes]
        
        # Randomly select an outcome based on weights
        outcome = random.choices(outcomes, weights=weights, k=1)[0]
        
        # Get the status code and HTTP status for this outcome
        status_code = cls.OUTCOMES[outcome]['code']
        http_status = cls.OUTCOMES[outcome]['http_status']
        
        # Format name and description
        name = outcome.replace('_', ' ').title()
        description = f"Verification {outcome.replace('_', ' ')}"
        
        return outcome, status_code, http_status, name, description
    
    @classmethod
    def get_response_for_outcome(cls, outcome, request_id, status_code):
        """
        Get the appropriate response data for an outcome
        """
        base_response = {
            'request_id': request_id,
            'code': status_code
        }
        
        if outcome == 'success':
            return {
                **base_response,
                'status': 'success',
                'message': 'Aadhar verification successful'
            }
        elif outcome == 'pending':
            return {
                **base_response,
                'status': 'pending',
                'message': 'Verification in progress. Check status later.'
            }
        elif outcome == 'not_found':
            return {
                **base_response,
                'status': 'error',
                'message': 'Aadhar number not found in database'
            }
        elif outcome == 'server_error':
            return {
                **base_response,
                'status': 'error',
                'message': 'Internal server error during verification'
            }
        else:  # timeout
            return {
                **base_response,
                'status': 'error',
                'message': 'Verification request timed out'
            }