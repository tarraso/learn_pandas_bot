from django.db import models


class TelegramUser(models.Model):
    """Represents a Telegram user using the bot"""
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=32, null=True, blank=True)
    first_name = models.CharField(max_length=64, null=True, blank=True)
    last_name = models.CharField(max_length=64, null=True, blank=True)
    language_code = models.CharField(max_length=10, null=True, blank=True)
    is_bot = models.BooleanField(default=False)

    # User preferences
    current_topic = models.ForeignKey(
        'questions.Topic',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )
    difficulty_level = models.CharField(
        max_length=20,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
        ],
        default='beginner'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Telegram User'
        verbose_name_plural = 'Telegram Users'

    def __str__(self):
        return f"{self.first_name} ({self.telegram_id})"


class QuestionHistory(models.Model):
    """Tracks which questions a user has answered"""
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='question_history')
    question = models.ForeignKey('questions.Question', on_delete=models.CASCADE)
    is_correct = models.BooleanField(default=False)
    user_answer = models.TextField(blank=True)
    answered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Question History'
        verbose_name_plural = 'Question History'
        ordering = ['-answered_at']

    def __str__(self):
        return f"{self.user} - {self.question} ({'✓' if self.is_correct else '✗'})"


class UserProgress(models.Model):
    """Tracks user progress on specific topics"""
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name='progress')
    topic = models.ForeignKey('questions.Topic', on_delete=models.CASCADE)
    questions_attempted = models.IntegerField(default=0)
    questions_correct = models.IntegerField(default=0)
    documentation_viewed = models.BooleanField(default=False, help_text="Has user viewed the documentation for this topic")
    last_activity = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User Progress'
        verbose_name_plural = 'User Progress'
        unique_together = ('user', 'topic')

    def __str__(self):
        return f"{self.user} - {self.topic} ({self.questions_correct}/{self.questions_attempted})"

    @property
    def accuracy(self):
        """Calculate accuracy percentage"""
        if self.questions_attempted == 0:
            return 0
        return (self.questions_correct / self.questions_attempted) * 100
