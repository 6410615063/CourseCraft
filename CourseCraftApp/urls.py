from django.urls import path
from . import views

app_name = 'CourseCraftApp'

urlpatterns = [
    path('', views.index, name='index')
] 