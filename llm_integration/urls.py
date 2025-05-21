from django.urls import path
from . import views

app_name = 'llm_integration'

urlpatterns = [
    path('test-llm-gemini/', views.test_llm_gemini, name='test_llm_gemini'),
] 