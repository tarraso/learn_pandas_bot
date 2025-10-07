"""API views for Telegram Mini App."""
import io
import sys
from contextlib import redirect_stdout, redirect_stderr

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from asgiref.sync import sync_to_async
import json

from questions.models import Topic, Question
from bot.models import TelegramUser, QuestionHistory
from bot.utils import get_next_question as get_next_question_util


@csrf_exempt
@require_http_methods(["GET"])
def topics_list(request):
    """Get list of all topics."""
    topics = Topic.objects.all().values('id', 'name', 'description', 'documentation')
    return JsonResponse(list(topics), safe=False)


@csrf_exempt
@require_http_methods(["GET"])
def next_question_view(request):
    """Get next question for user."""
    user_id = request.GET.get('user_id')
    topic_id = request.GET.get('topic_id')

    if not user_id:
        return JsonResponse({'error': 'user_id required'}, status=400)

    try:
        user = TelegramUser.objects.select_related('current_topic').get(telegram_id=user_id)
    except TelegramUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

    # Get topic
    topic = None
    if topic_id:
        try:
            topic = Topic.objects.get(id=topic_id)
        except Topic.DoesNotExist:
            pass

    if not topic:
        topic = user.current_topic

    # Get correct question IDs answered
    correct_ids = QuestionHistory.objects.filter(
        user=user,
        is_correct=True
    ).values_list('question_id', flat=True)

    # Get questions
    query = Question.objects.filter(
        is_active=True,
        question_type='multiple_choice'
    ).select_related('topic')

    if topic:
        query = query.filter(topic=topic)

    query = query.filter(difficulty=user.difficulty_level)
    query = query.exclude(id__in=correct_ids)

    question = query.first()

    if not question:
        return JsonResponse({'error': 'No questions available'}, status=404)

    return JsonResponse({
        'id': question.id,
        'topic': question.topic.name,
        'difficulty': question.difficulty,
        'question_text': question.question_text,
        'code_example': question.code_example,
        'options': question.get_options(),
        'correct_option': question.correct_option,
        'explanation': question.explanation,
        'documentation_link': question.documentation_link,
    })


@csrf_exempt
@require_http_methods(["POST"])
def answer_question_view(request):
    """Submit answer to question."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user_id = data.get('user_id')
    question_id = data.get('question_id')
    answer = data.get('answer')

    if not all([user_id, question_id, answer]):
        return JsonResponse({'error': 'Missing required fields'}, status=400)

    try:
        user = TelegramUser.objects.get(telegram_id=user_id)
        question = Question.objects.get(id=question_id)
    except (TelegramUser.DoesNotExist, Question.DoesNotExist) as e:
        return JsonResponse({'error': str(e)}, status=404)

    is_correct = answer == question.correct_option

    # Record answer
    QuestionHistory.objects.create(
        user=user,
        question=question,
        is_correct=is_correct,
        user_answer=answer
    )

    return JsonResponse({
        'success': True,
        'is_correct': is_correct
    })


@csrf_exempt
@require_http_methods(["POST"])
def run_code_view(request):
    """Execute Python pandas code safely."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    code = data.get('code', '')

    if not code:
        return JsonResponse({'error': 'No code provided'}, status=400)

    # Capture stdout and stderr
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    try:
        # Create a restricted namespace
        namespace = {
            '__builtins__': {
                'print': print,
                'len': len,
                'range': range,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'tuple': tuple,
                'set': set,
                'True': True,
                'False': False,
                'None': None,
            }
        }

        # Import pandas in namespace
        exec('import pandas as pd', namespace)
        exec('import numpy as np', namespace)

        # Execute code
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            exec(code, namespace)

        output = stdout_capture.getvalue()
        errors = stderr_capture.getvalue()

        if errors:
            return JsonResponse({
                'success': False,
                'error': errors
            })

        return JsonResponse({
            'success': True,
            'output': output or 'Code executed successfully (no output)'
        })

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'{type(e).__name__}: {str(e)}'
        })
