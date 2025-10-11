"""DRF API views for Telegram Mini App."""
import io
from contextlib import redirect_stdout, redirect_stderr

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from questions.models import Topic, Question
from bot.models import TelegramUser, QuestionHistory
from .serializers import (
    TopicSerializer,
    QuestionSerializer,
    AnswerSubmissionSerializer,
    CodeExecutionSerializer,
    CodeExecutionResponseSerializer,
    UserStatsSerializer,
    CodeTaskSerializer,
    CodeSubmissionSerializer,
    CodeSubmissionResponseSerializer,
)


class TopicViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing topics.
    Provides list and retrieve actions.
    """
    queryset = Topic.objects.all().order_by('order', 'name')
    serializer_class = TopicSerializer


class QuestionAPIView(APIView):
    """
    API view for getting next question for user.
    """

    def get(self, request):
        """Get next unanswered question for user."""
        user_id = request.query_params.get('user_id')
        topic_id = request.query_params.get('topic_id')

        if not user_id:
            return Response(
                {'error': 'user_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get user
        try:
            user = TelegramUser.objects.select_related('current_topic').get(telegram_id=user_id)
        except TelegramUser.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get topic
        topic = None
        if topic_id:
            try:
                topic = Topic.objects.get(id=topic_id)
            except Topic.DoesNotExist:
                pass

        if not topic:
            topic = user.current_topic

        # Get correctly answered question IDs
        correct_ids = QuestionHistory.objects.filter(
            user=user,
            is_correct=True
        ).values_list('question_id', flat=True)

        # Build query for next question
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
            return Response(
                {'error': 'No questions available'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = QuestionSerializer(question)
        return Response(serializer.data)


class AnswerQuestionAPIView(APIView):
    """
    API view for submitting answers to questions.
    """

    def post(self, request):
        """Submit an answer to a question."""
        serializer = AnswerSubmissionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get validated data
        user_id = serializer.validated_data['user_id']
        question_id = serializer.validated_data['question_id']
        answer = serializer.validated_data['answer']

        # Get user and question
        try:
            user = TelegramUser.objects.get(telegram_id=user_id)
        except TelegramUser.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response(
                {'error': 'Question not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if correct
        is_correct = answer == question.correct_option

        # Record answer
        QuestionHistory.objects.create(
            user=user,
            question=question,
            is_correct=is_correct,
            user_answer=answer
        )

        return Response({
            'success': True,
            'is_correct': is_correct,
            'correct_option': question.correct_option,
            'explanation': question.explanation,
        })


class CodeExecutionAPIView(APIView):
    """
    API view for executing Python/Pandas code safely.
    """

    def post(self, request):
        """Execute code and return result."""
        serializer = CodeExecutionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        code = serializer.validated_data['code']

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
                    'bool': bool,
                    'True': True,
                    'False': False,
                    'None': None,
                    'enumerate': enumerate,
                    'zip': zip,
                    'map': map,
                    'filter': filter,
                    'sorted': sorted,
                    'sum': sum,
                    'min': min,
                    'max': max,
                }
            }

            # Import pandas and numpy
            exec('import pandas as pd', namespace)
            exec('import numpy as np', namespace)

            # Execute code
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                exec(code, namespace)

            output = stdout_capture.getvalue()
            errors = stderr_capture.getvalue()

            if errors:
                response_serializer = CodeExecutionResponseSerializer(data={
                    'success': False,
                    'error': errors
                })
            else:
                response_serializer = CodeExecutionResponseSerializer(data={
                    'success': True,
                    'output': output or 'Code executed successfully (no output)'
                })

            response_serializer.is_valid(raise_exception=True)
            return Response(response_serializer.data)

        except Exception as e:
            response_serializer = CodeExecutionResponseSerializer(data={
                'success': False,
                'error': f'{type(e).__name__}: {str(e)}'
            })
            response_serializer.is_valid(raise_exception=True)
            return Response(response_serializer.data)


class UserStatsAPIView(APIView):
    """
    API view for getting user statistics.
    """

    def get(self, request):
        """Get statistics for a user."""
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response(
                {'error': 'user_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = TelegramUser.objects.get(telegram_id=user_id)
        except TelegramUser.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get stats
        history = QuestionHistory.objects.filter(user=user)
        total = history.count()
        correct = history.filter(is_correct=True).count()
        accuracy = (correct / total * 100) if total > 0 else 0

        # Per-topic stats
        topics_stats = []
        for topic in Topic.objects.all():
            topic_history = history.filter(question__topic=topic)
            topic_total = topic_history.count()
            if topic_total > 0:
                topic_correct = topic_history.filter(is_correct=True).count()
                topics_stats.append({
                    'topic': topic.name,
                    'attempted': topic_total,
                    'correct': topic_correct,
                    'accuracy': round(topic_correct / topic_total * 100, 1)
                })

        stats_data = {
            'total_questions': total,
            'correct_answers': correct,
            'accuracy': round(accuracy, 1),
            'topics': topics_stats
        }

        serializer = UserStatsSerializer(data=stats_data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)


class CodeTaskAPIView(APIView):
    """
    API view for getting code challenge tasks.
    """

    def get(self, request):
        """Get next code challenge for user."""
        user_id = request.query_params.get('user_id')
        topic_id = request.query_params.get('topic_id')

        if not user_id:
            return Response(
                {'error': 'user_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get user
        try:
            user = TelegramUser.objects.select_related('current_topic').get(telegram_id=user_id)
        except TelegramUser.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get topic
        topic = None
        if topic_id:
            try:
                topic = Topic.objects.get(id=topic_id)
            except Topic.DoesNotExist:
                pass

        if not topic:
            topic = user.current_topic

        # Get correctly solved task IDs
        correct_ids = QuestionHistory.objects.filter(
            user=user,
            is_correct=True
        ).values_list('question_id', flat=True)

        # Build query for next task
        query = Question.objects.filter(
            is_active=True,
            question_type='code'
        ).select_related('topic')

        if topic:
            query = query.filter(topic=topic)

        query = query.filter(difficulty=user.difficulty_level)
        query = query.exclude(id__in=correct_ids)

        task = query.first()

        if not task:
            return Response(
                {'error': 'No code tasks available'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CodeTaskSerializer(task)
        return Response(serializer.data)


class CodeSubmissionAPIView(APIView):
    """
    API view for submitting code challenge solutions.
    """

    def post(self, request):
        """Submit a code solution and check it."""
        serializer = CodeSubmissionSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get validated data
        user_id = serializer.validated_data['user_id']
        question_id = serializer.validated_data['question_id']
        code = serializer.validated_data['code']

        # Get user and question
        try:
            user = TelegramUser.objects.get(telegram_id=user_id)
        except TelegramUser.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            task = Question.objects.get(id=question_id, question_type='code')
        except Question.DoesNotExist:
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Run test cases
        test_results = []
        all_passed = True

        if task.test_cases:
            for i, test_case in enumerate(task.test_cases):
                try:
                    # Create namespace with pandas and numpy
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
                            'bool': bool,
                            'True': True,
                            'False': False,
                            'None': None,
                            'enumerate': enumerate,
                            'zip': zip,
                            'map': map,
                            'filter': filter,
                            'sorted': sorted,
                            'sum': sum,
                            'min': min,
                            'max': max,
                        }
                    }

                    exec('import pandas as pd', namespace)
                    exec('import numpy as np', namespace)

                    # Set up test input if provided
                    if 'setup' in test_case:
                        exec(test_case['setup'], namespace)

                    # Execute user's code
                    exec(code, namespace)

                    # Get the result variable
                    result_var = test_case.get('result_var', 'result')
                    actual_output = namespace.get(result_var)

                    # Compare with expected output
                    expected = test_case['expected_output']

                    # Handle pandas objects comparison
                    if 'pandas' in str(type(actual_output)):
                        import pandas as pd
                        if isinstance(actual_output, pd.DataFrame) or isinstance(actual_output, pd.Series):
                            passed = actual_output.equals(eval(expected, namespace))
                        else:
                            passed = str(actual_output) == str(eval(expected, namespace))
                    else:
                        passed = str(actual_output) == str(eval(expected, namespace))

                    test_results.append({
                        'test_number': i + 1,
                        'passed': passed,
                        'expected': str(expected),
                        'actual': str(actual_output)
                    })

                    if not passed:
                        all_passed = False

                except Exception as e:
                    test_results.append({
                        'test_number': i + 1,
                        'passed': False,
                        'error': f'{type(e).__name__}: {str(e)}'
                    })
                    all_passed = False

        # Record submission
        QuestionHistory.objects.create(
            user=user,
            question=task,
            is_correct=all_passed,
            user_answer=code
        )

        response_data = {
            'success': True,
            'passed': all_passed,
            'test_results': test_results,
        }

        if all_passed:
            response_data['explanation'] = task.explanation

        response_serializer = CodeSubmissionResponseSerializer(data=response_data)
        response_serializer.is_valid(raise_exception=True)
        return Response(response_serializer.data)
