from django.db import models


class Topic(models.Model):
    """Represents a topic in pandas (e.g., DataFrames, Series, GroupBy, etc.)"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    documentation = models.TextField(blank=True, help_text="Detailed documentation/learning material for this topic")
    order = models.IntegerField(default=0, help_text="Order in which topics should be presented")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'name']
        verbose_name = 'Topic'
        verbose_name_plural = 'Topics'

    def __str__(self):
        return self.name


class Question(models.Model):
    """Represents a question about pandas"""

    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'),
        ('code', 'Code Challenge'),
        ('explanation', 'Explanation'),
        ('fill_blank', 'Fill in the Blank'),
    ]

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='multiple_choice')
    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')

    # Question content
    question_text = models.TextField(help_text="The question to ask the user")
    code_example = models.TextField(blank=True, help_text="Optional code example to show with the question")

    # Answer options (for multiple choice)
    option_a = models.TextField(blank=True)
    option_b = models.TextField(blank=True)
    option_c = models.TextField(blank=True)
    option_d = models.TextField(blank=True)
    correct_option = models.CharField(max_length=1, blank=True, help_text="A, B, C, or D")

    # For code challenges and fill in the blank
    correct_answer = models.TextField(blank=True, help_text="Correct answer for code/fill blank questions")

    # Explanation
    explanation = models.TextField(help_text="Explanation of the correct answer")
    documentation_link = models.URLField(blank=True, help_text="Link to pandas documentation")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['topic', 'difficulty', 'created_at']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    def __str__(self):
        return f"{self.topic.name} - {self.question_type} - {self.difficulty}"

    def get_options(self):
        """Return a list of non-empty options"""
        options = []
        if self.option_a:
            options.append(('A', self.option_a))
        if self.option_b:
            options.append(('B', self.option_b))
        if self.option_c:
            options.append(('C', self.option_c))
        if self.option_d:
            options.append(('D', self.option_d))
        return options


class Snippet(models.Model):
    """Useful pandas code snippets to share with users"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    code = models.TextField()
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='snippets')
    difficulty = models.CharField(
        max_length=20,
        choices=Question.DIFFICULTY_CHOICES,
        default='beginner'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['topic', 'difficulty', 'title']
        verbose_name = 'Code Snippet'
        verbose_name_plural = 'Code Snippets'

    def __str__(self):
        return f"{self.topic.name} - {self.title}"
