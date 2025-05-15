from django.urls import path
from . import views

app_name = 'course_generation'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('chapter/<int:chapter_id>/', views.chapter_detail, name='chapter_detail'),
    path('update-knowledge/', views.update_knowledge, name='update_knowledge'),
    path('generate-course/', views.generate_course_view, name='generate_course'),
] 