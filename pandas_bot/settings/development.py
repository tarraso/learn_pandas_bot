"""
Development settings for pandas_bot project.
"""
import os
import dj_database_url
from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '.ngrok-free.app', 'pandadev.taras.rocks']

# Database - use SQLite for development or PostgreSQL if DATABASE_URL is set
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR}/db.sqlite3',
        conn_max_age=600
    )
}

# CORS settings for development
CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]

# Allow all origins in development (easier testing with ngrok)
if os.environ.get('NGROK_URL'):
    CORS_ALLOWED_ORIGINS.append(os.environ.get('NGROK_URL'))

CORS_ALLOW_CREDENTIALS = True

# Disable CSRF for easier development
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:3000',
    'http://127.0.0.1:3000',
]

if os.environ.get('NGROK_URL'):
    CSRF_TRUSTED_ORIGINS.append(os.environ.get('NGROK_URL'))
