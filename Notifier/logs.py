import logging
from .models import FailureLog

logger = logging.getLogger(__name__)

def get_failure_logs():
    # Fetch failure logs
    return FailureLog.objects.all().order_by('-timestamp')
