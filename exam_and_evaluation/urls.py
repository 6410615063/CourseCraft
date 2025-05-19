from django.urls import path
from . import views

app_name = 'exam_and_evaluation'

urlpatterns = [
    path('exam/<int:course_id>/<str:is_final_str>/', views.exam_view, name='exam'),
    path('exercise/<int:chapter_id>/', views.exercise_view, name='exercise'),
]