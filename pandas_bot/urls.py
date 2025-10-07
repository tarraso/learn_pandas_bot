"""URL Configuration for pandas_bot project."""

from django.contrib import admin
from django.urls import path, include
from .health import health_check, readiness_check, liveness_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bot/', include('bot.urls')),
    path('api/', include('api.urls')),

    # Health check endpoints
    path('health/', health_check, name='health_check'),
    path('ready/', readiness_check, name='readiness_check'),
    path('live/', liveness_check, name='liveness_check'),
]
