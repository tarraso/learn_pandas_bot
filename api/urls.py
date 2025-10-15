"""API URLs."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views_drf

# Create router for ViewSets
router = DefaultRouter()
router.register(r'topics', views_drf.TopicViewSet, basename='topic')

urlpatterns = [
    # Router URLs (includes /topics/ and /topics/<id>/)
    path('', include(router.urls)),

    # Custom API views
    path('questions/next/', views_drf.QuestionAPIView.as_view(), name='next_question'),
    path('questions/answer/', views_drf.AnswerQuestionAPIView.as_view(), name='answer_question'),
    path('code/task/', views_drf.CodeTaskAPIView.as_view(), name='code_task'),
    path('users/stats/', views_drf.UserStatsAPIView.as_view(), name='user_stats'),
]
