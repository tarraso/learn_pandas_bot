"""
Initialize Django for standalone scripts.
Import this module at the beginning of any standalone script that needs Django models.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pandas_bot.settings')
django.setup()
