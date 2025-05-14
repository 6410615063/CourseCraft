from django.urls import path
from . import views

app_name = 'course_generation'

urlpatterns = [
    path('generate/', views.generate_course, name='generate_course'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),
] 