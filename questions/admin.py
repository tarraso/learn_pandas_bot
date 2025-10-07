from django.contrib import admin
from .models import Topic, Question, Snippet


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'created_at')
    list_editable = ('order',)
    search_fields = ('name', 'description')
    ordering = ('order', 'name')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_type', 'topic', 'difficulty', 'is_active', 'created_at')
    list_filter = ('topic', 'difficulty', 'question_type', 'is_active')
    search_fields = ('question_text', 'explanation')
    list_editable = ('is_active',)
    ordering = ('topic', 'difficulty', 'created_at')

    fieldsets = (
        ('Basic Information', {
            'fields': ('topic', 'question_type', 'difficulty', 'is_active')
        }),
        ('Question', {
            'fields': ('question_text', 'code_example')
        }),
        ('Multiple Choice Options', {
            'fields': ('option_a', 'option_b', 'option_c', 'option_d', 'correct_option'),
            'classes': ('collapse',)
        }),
        ('Answer', {
            'fields': ('correct_answer', 'explanation', 'documentation_link')
        }),
    )


@admin.register(Snippet)
class SnippetAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'difficulty', 'created_at')
    list_filter = ('topic', 'difficulty')
    search_fields = ('title', 'description', 'code')
    ordering = ('topic', 'difficulty', 'title')
