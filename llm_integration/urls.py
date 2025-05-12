from django.urls import path
from . import views

app_name = 'llm_integration'

urlpatterns = [
    path('test-credentials/', views.test_credentials, name='test_credentials'),
    path('test-llm-curl/', views.test_llm, name='test_llm_curl'),
    path('test-llm-gemini/', views.test_llm_gemini, name='test_llm_gemini'),
] 