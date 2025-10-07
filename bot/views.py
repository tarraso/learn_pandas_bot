from django.http import JsonResponse


def webhook(request):
    """Webhook endpoint for Telegram (if needed for webhooks instead of polling)"""
    return JsonResponse({'status': 'ok'})
