from django.contrib import admin
from .models import Topic, Question, Snippet, Dataset, QuestionDataset


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'created_at')
    list_editable = ('order',)
    search_fields = ('name', 'description')
    ordering = ('order', 'name')


class QuestionDatasetInline(admin.TabularInline):
    """Inline для управления датасетами и ожидаемыми результатами внутри вопроса"""
    model = QuestionDataset
    extra = 1
    fields = ('dataset', 'expected_result', 'description', 'order')
    verbose_name = "Датасет с ожидаемым результатом"
    verbose_name_plural = "Датасеты с ожидаемыми результатами"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_type', 'topic', 'difficulty', 'is_active', 'get_datasets_count', 'created_at')
    list_filter = ('topic', 'difficulty', 'question_type', 'is_active')
    search_fields = ('question_text', 'explanation')
    list_editable = ('is_active',)
    ordering = ('topic', 'difficulty', 'created_at')
    inlines = [QuestionDatasetInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('topic', 'question_type', 'difficulty', 'is_active')
        }),
        ('Вопрос', {
            'fields': ('question_text', 'code_example')
        }),
        ('Варианты ответов (Multiple Choice)', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'correct_option'),
            'classes': ('collapse',)
        }),
        ('Кодовое задание (Code Challenge)', {
            'fields': ('starter_code', 'test_cases', 'hint'),
            'classes': ('collapse',),
            'description': 'Настройки для кодовых заданий. Датасеты добавляйте ниже в разделе "Датасеты с ожидаемыми результатами".'
        }),
        ('Ответ и объяснение', {
            'fields': ('correct_answer', 'explanation', 'documentation_link')
        }),
    )

    def get_datasets_count(self, obj):
        return obj.datasets.count()
    get_datasets_count.short_description = 'Датасетов'


@admin.register(Snippet)
class SnippetAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'difficulty', 'created_at')
    list_filter = ('topic', 'difficulty')
    search_fields = ('title', 'description', 'code')
    ordering = ('topic', 'difficulty', 'title')


@admin.register(QuestionDataset)
class QuestionDatasetAdmin(admin.ModelAdmin):
    """Админка для управления связями вопрос-датасет"""
    list_display = ('get_question_short', 'dataset', 'get_result_preview', 'order', 'created_at')
    list_filter = ('question__topic', 'question__difficulty', 'dataset')
    search_fields = ('question__question_text', 'dataset__name', 'description')
    ordering = ('question', 'order')

    fieldsets = (
        ('Связь', {
            'fields': ('question', 'dataset', 'order')
        }),
        ('Ожидаемый результат', {
            'fields': ('expected_result', 'description'),
            'description': 'Укажите ожидаемый результат в JSON формате. Примеры:<br>'
                          '• DataFrame: {"col1": [1, 2], "col2": [3, 4]}<br>'
                          '• Series: [1, 2, 3, 4]<br>'
                          '• Скаляр: 42 или "текст"<br>'
                          '• Boolean: true / false'
        }),
    )

    def get_question_short(self, obj):
        return obj.question.question_text[:50] + "..."
    get_question_short.short_description = 'Вопрос'

    def get_result_preview(self, obj):
        result_str = str(obj.expected_result)
        return result_str[:50] + "..." if len(result_str) > 50 else result_str
    get_result_preview.short_description = 'Ожидаемый результат'


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ('name', 'data_format', 'is_active', 'get_questions_count', 'created_at')
    list_filter = ('data_format', 'is_active')
    search_fields = ('name', 'description')
    list_editable = ('is_active',)
    ordering = ('name',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Данные', {
            'fields': ('data', 'data_format'),
            'description': 'JSON формат данных. Примеры:<br>'
                          '• Dictionary: {"col1": [1, 2], "col2": [3, 4]}<br>'
                          '• List of dicts: [{"name": "A", "value": 1}, {"name": "B", "value": 2}]<br>'
                          '• CSV string: "name,value\\nA,1\\nB,2"'
        }),
    )

    def get_questions_count(self, obj):
        return obj.questions.count()
    get_questions_count.short_description = 'Вопросов'
