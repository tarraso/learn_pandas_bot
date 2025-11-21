"""Utility functions for the bot."""
import random
from asgiref.sync import sync_to_async
from django.db.models import Q, Count
from .models import TelegramUser, QuestionHistory, UserProgress
from questions.models import Question, Topic


@sync_to_async
def get_or_create_user(telegram_user):
    """Get or create a TelegramUser from telegram.User object."""
    # Get default topic (may be None if no topics exist)
    default_topic = Topic.get_default()
    
    user, created = TelegramUser.objects.select_related('current_topic').get_or_create(
        telegram_id=telegram_user.id,
        defaults={
            'username': telegram_user.username,
            'first_name': telegram_user.first_name,
            'last_name': telegram_user.last_name,
            'language_code': telegram_user.language_code,
            'is_bot': telegram_user.is_bot,
            'current_topic': default_topic  # Will be None if no topics exist
        }
    )
    # If not created, fetch with select_related
    if not created:
        user = TelegramUser.objects.select_related('current_topic').get(telegram_id=telegram_user.id)
    return user, created


@sync_to_async
def get_next_question(user, topic=None, difficulty=None):
    """
    Get the next question for a user.
    Prioritizes questions they haven't seen or got wrong.
    """
    # Use user's preferences if not specified
    if topic is None:
        topic = user.current_topic
    if difficulty is None:
        difficulty = user.difficulty_level

    # Get questions the user has answered correctly
    correct_question_ids = QuestionHistory.objects.filter(
        user=user,
        is_correct=True
    ).values_list('question_id', flat=True)

    # Build query
    query = Q(is_active=True)
    if topic:
        query &= Q(topic=topic)
    if difficulty:
        query &= Q(difficulty=difficulty)

    # Exclude correctly answered questions
    questions = Question.objects.filter(query).exclude(id__in=correct_question_ids).select_related('topic')

    if not questions.exists():
        # If all questions are answered correctly, return a random one
        questions = Question.objects.filter(query).select_related('topic')

    if not questions.exists():
        return None

    # Return a random question from the filtered set
    return random.choice(list(questions))


@sync_to_async
def record_answer(user, question, user_answer, is_correct):
    """Record a user's answer to a question."""
    # Create history entry
    QuestionHistory.objects.create(
        user=user,
        question=question,
        is_correct=is_correct,
        user_answer=user_answer
    )

    # Update user progress
    progress, created = UserProgress.objects.get_or_create(
        user=user,
        topic=question.topic,
        defaults={
            'questions_attempted': 0,
            'questions_correct': 0
        }
    )
    progress.questions_attempted += 1
    if is_correct:
        progress.questions_correct += 1
    progress.save()


@sync_to_async
def get_user_stats(user):
    """Get statistics for a user."""
    total_questions = QuestionHistory.objects.filter(user=user).count()
    correct_answers = QuestionHistory.objects.filter(user=user, is_correct=True).count()

    topic_stats = UserProgress.objects.filter(user=user).select_related('topic')

    stats = {
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'accuracy': (correct_answers / total_questions * 100) if total_questions > 0 else 0,
        'topics': []
    }

    for progress in topic_stats:
        stats['topics'].append({
            'topic': progress.topic.name,
            'attempted': progress.questions_attempted,
            'correct': progress.questions_correct,
            'accuracy': progress.accuracy
        })

    return stats


@sync_to_async
def get_all_topics():
    """Get all available topics."""
    return list(Topic.objects.all().order_by('order'))


@sync_to_async
def set_user_topic(user, topic_name):
    """Set the user's current topic."""
    try:
        topic = Topic.objects.get(name=topic_name)
        user.current_topic = topic
        user.save()
        return topic
    except Topic.DoesNotExist:
        return None


@sync_to_async
def set_user_difficulty(user, difficulty):
    """Set the user's difficulty level."""
    if difficulty in ['beginner', 'intermediate', 'advanced']:
        user.difficulty_level = difficulty
        user.save()
        return True
    return False


@sync_to_async
def check_documentation_viewed(user, topic):
    """Check if user has viewed documentation for a topic."""
    try:
        progress = UserProgress.objects.get(user=user, topic=topic)
        return progress.documentation_viewed
    except UserProgress.DoesNotExist:
        return False


@sync_to_async
def mark_documentation_viewed(user, topic):
    """Mark documentation as viewed for a topic."""
    progress, created = UserProgress.objects.get_or_create(
        user=user,
        topic=topic,
        defaults={
            'questions_attempted': 0,
            'questions_correct': 0
        }
    )
    progress.documentation_viewed = True
    progress.save()
    return progress


@sync_to_async
def get_topic_by_id(topic_id):
    """Get topic by id."""
    try:
        return Topic.objects.get(id=topic_id)
    except Topic.DoesNotExist:
        return None
