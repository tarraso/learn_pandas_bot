"""API URLs."""
from django.urls import path
from . import views

urlpatterns = [
    path('topics/', views.topics_list, name='api_topics'),
    path('next-question/', views.next_question_view, name='api_next_question'),
    path('answer-question/', views.answer_question_view, name='api_answer_question'),
    path('run-code/', views.run_code_view, name='api_run_code'),
]
