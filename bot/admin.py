from django.contrib import admin
from .models import TelegramUser, QuestionHistory, UserProgress


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('telegram_id', 'first_name', 'username', 'difficulty_level', 'current_topic', 'created_at')
    list_filter = ('difficulty_level', 'current_topic', 'created_at')
    search_fields = ('telegram_id', 'username', 'first_name', 'last_name')
    ordering = ('-created_at',)


@admin.register(QuestionHistory)
class QuestionHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'is_correct', 'answered_at')
    list_filter = ('is_correct', 'answered_at', 'question__topic')
    search_fields = ('user__username', 'user__first_name', 'question__question_text')
    ordering = ('-answered_at',)
    readonly_fields = ('answered_at',)


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'topic', 'questions_attempted', 'questions_correct', 'accuracy', 'last_activity')
    list_filter = ('topic', 'last_activity')
    search_fields = ('user__username', 'user__first_name', 'topic__name')
    ordering = ('-last_activity',)
    readonly_fields = ('last_activity',)

    def accuracy(self, obj):
        return f"{obj.accuracy:.1f}%"
    accuracy.short_description = 'Accuracy'
