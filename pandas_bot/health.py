"""
Health check views for monitoring application status.
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


def health_check(request):
    """
    Simple health check endpoint.
    Returns 200 OK if the application is healthy.
    """
    status = {
        'status': 'healthy',
        'checks': {}
    }
    http_status = 200

    # Check database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status['checks']['database'] = 'ok'
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        status['checks']['database'] = 'error'
        status['status'] = 'unhealthy'
        http_status = 503

    return JsonResponse(status, status=http_status)


def readiness_check(request):
    """
    Readiness check for Kubernetes/Docker.
    Checks if the application is ready to serve traffic.
    """
    # Similar to health check but can include additional checks
    return health_check(request)


def liveness_check(request):
    """
    Liveness check for Kubernetes/Docker.
    Simple check that the application process is running.
    """
    return JsonResponse({'status': 'alive'}, status=200)
