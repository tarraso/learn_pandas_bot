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

    @classmethod
    def get_default(cls):
        """Get the default topic (first by order)."""
        return cls.objects.order_by('order', 'name').first()


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

    # For code challenges - test cases and starter code
    starter_code = models.TextField(blank=True, help_text="Initial code template for code challenges")
    test_cases = models.JSONField(
        blank=True,
        null=True,
        help_text="JSON array of test cases with 'input', 'expected_output' for validation"
    )
    hint = models.TextField(blank=True, help_text="Optional hint for code challenges")

    # Datasets for code challenges
    datasets = models.ManyToManyField(
        'Dataset',
        through='QuestionDataset',
        related_name='questions',
        blank=True,
        help_text="Датасеты для проверки кодового задания"
    )

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

    def get_datasets_data(self):
        """Возвращает список данных из всех связанных датасетов"""
        return [dataset.data for dataset in self.datasets.filter(is_active=True)]

    def has_datasets(self):
        """Проверяет, есть ли у вопроса датасеты"""
        return self.datasets.filter(is_active=True).exists()


class QuestionDataset(models.Model):
    """Промежуточная модель для связи вопросов с датасетами и хранения ожидаемых результатов"""

    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name="Вопрос")
    dataset = models.ForeignKey('Dataset', on_delete=models.CASCADE, verbose_name="Датасет")
    expected_result = models.JSONField(
        help_text="Ожидаемый результат выполнения кода на этом датасете (DataFrame в виде dict, строка, число и т.д.)"
    )
    description = models.TextField(
        blank=True,
        help_text="Описание что должно получиться при выполнении кода"
    )
    order = models.IntegerField(default=0, help_text="Порядок выполнения теста")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['question', 'order']
        verbose_name = 'Вопрос-Датасет'
        verbose_name_plural = 'Вопросы-Датасеты'
        unique_together = [['question', 'dataset']]

    def __str__(self):
        return f"{self.question.question_text[:30]}... → {self.dataset.name}"


class Dataset(models.Model):
    """Datasets for testing code challenges"""

    FORMAT_CHOICES = [
        ('dict', 'Python Dictionary'),
        ('json', 'JSON String'),
        ('csv', 'CSV String'),
    ]

    name = models.CharField(max_length=200, help_text="Название датасета")
    description = models.TextField(blank=True, help_text="Описание датасета и его содержимого")
    data = models.JSONField(help_text="Данные в JSON формате (словарь, список словарей, или строка)")
    data_format = models.CharField(
        max_length=20,
        choices=FORMAT_CHOICES,
        default='dict',
        help_text="Формат данных для использования в коде"
    )

    # Метаданные
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True, help_text="Активен ли датасет")

    class Meta:
        ordering = ['name']
        verbose_name = 'Dataset'
        verbose_name_plural = 'Datasets'

    def __str__(self):
        return self.name

    def get_data_as_code(self):
        """Возвращает данные в виде строки кода Python для использования в тестах"""
        if self.data_format == 'dict':
            return repr(self.data)
        elif self.data_format == 'json':
            import json
            return f"'{json.dumps(self.data)}'"
        elif self.data_format == 'csv':
            # Если data содержит CSV строку
            if isinstance(self.data, str):
                return f"'{self.data}'"
            return repr(self.data)
        return repr(self.data)


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
