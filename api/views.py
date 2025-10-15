"""API views for Telegram Mini App."""
import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from questions.models import Topic, Question
from bot.models import TelegramUser, QuestionHistory


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


