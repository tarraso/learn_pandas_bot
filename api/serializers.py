"""API Serializers for Telegram Mini App."""
from rest_framework import serializers
from questions.models import Topic, Question
from bot.models import TelegramUser, QuestionHistory


class TopicSerializer(serializers.ModelSerializer):
    """Serializer for Topic model."""

    class Meta:
        model = Topic
        fields = ['id', 'name', 'description', 'documentation', 'order']


class QuestionOptionSerializer(serializers.Serializer):
    """Serializer for question options."""
    letter = serializers.CharField()
    text = serializers.CharField()


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model."""
    topic = serializers.StringRelatedField()
    options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            'id', 'topic', 'difficulty', 'question_text',
            'code_example', 'options', 'correct_option',
            'explanation', 'documentation_link'
        ]

    def get_options(self, obj):
        """Get formatted options."""
        return [
            {'letter': letter, 'text': text}
            for letter, text in obj.get_options()
        ]


class QuestionListSerializer(serializers.ModelSerializer):
    """Simplified serializer for question lists (without answer)."""
    topic = serializers.StringRelatedField()

    class Meta:
        model = Question
        fields = [
            'id', 'topic', 'difficulty', 'question_text',
            'code_example'
        ]


class AnswerSubmissionSerializer(serializers.Serializer):
    """Serializer for answer submission."""
    user_id = serializers.IntegerField()
    question_id = serializers.IntegerField()
    answer = serializers.CharField(max_length=1)

    def validate_answer(self, value):
        """Validate answer is a valid option letter."""
        if value not in ['A', 'B', 'C', 'D']:
            raise serializers.ValidationError("Answer must be A, B, C, or D")
        return value


class CodeExecutionSerializer(serializers.Serializer):
    """Serializer for code execution requests."""
    code = serializers.CharField()

    def validate_code(self, value):
        """Validate code is not empty and within size limits."""
        if not value.strip():
            raise serializers.ValidationError("Code cannot be empty")
        if len(value) > 10000:
            raise serializers.ValidationError("Code is too long (max 10000 characters)")
        return value


class CodeExecutionResponseSerializer(serializers.Serializer):
    """Serializer for code execution response."""
    success = serializers.BooleanField()
    output = serializers.CharField(required=False)
    error = serializers.CharField(required=False)


class UserStatsSerializer(serializers.Serializer):
    """Serializer for user statistics."""
    total_questions = serializers.IntegerField()
    correct_answers = serializers.IntegerField()
    accuracy = serializers.FloatField()
    topics = serializers.ListField(child=serializers.DictField())


class TelegramUserSerializer(serializers.ModelSerializer):
    """Serializer for TelegramUser model."""
    current_topic_name = serializers.CharField(source='current_topic.name', read_only=True)

    class Meta:
        model = TelegramUser
        fields = [
            'telegram_id', 'username', 'first_name', 'last_name',
            'difficulty_level', 'current_topic_name', 'created_at'
        ]
        read_only_fields = ['created_at']


class CodeTaskSerializer(serializers.ModelSerializer):
    """Serializer for code challenge tasks."""
    topic = serializers.StringRelatedField()

    class Meta:
        model = Question
        fields = [
            'id', 'topic', 'difficulty', 'question_text',
            'starter_code', 'test_cases', 'hint',
            'explanation', 'documentation_link'
        ]


class CodeSubmissionSerializer(serializers.Serializer):
    """Serializer for code challenge submission."""
    user_id = serializers.IntegerField()
    question_id = serializers.IntegerField()
    code = serializers.CharField()

    def validate_code(self, value):
        """Validate code is not empty and within size limits."""
        if not value.strip():
            raise serializers.ValidationError("Code cannot be empty")
        if len(value) > 10000:
            raise serializers.ValidationError("Code is too long (max 10000 characters)")
        return value


class CodeSubmissionResponseSerializer(serializers.Serializer):
    """Serializer for code submission response."""
    success = serializers.BooleanField()
    passed = serializers.BooleanField()
    test_results = serializers.ListField(child=serializers.DictField())
    explanation = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
