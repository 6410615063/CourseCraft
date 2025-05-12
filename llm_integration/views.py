from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from .llm_caller import LLMCaller as OriginalLLMCaller
from .llm_caller_2 import LLMCaller as CurlLLMCaller
from .llm_caller_3 import LLMCaller as GeminiLLMCaller
import logging

logger = logging.getLogger(__name__)

# Create your views here.

def test_credentials(request):
    """
    Test view to verify Google Cloud credentials and LLM integration.
    """
    try:
        # Check if environment variables are set
        if not settings.GOOGLE_APPLICATION_CREDENTIALS:
            return JsonResponse({
                'status': 'error',
                'message': 'GOOGLE_APPLICATION_CREDENTIALS not set'
            }, status=500)
            
        if not settings.GOOGLE_CLOUD_PROJECT:
            return JsonResponse({
                'status': 'error',
                'message': 'GOOGLE_CLOUD_PROJECT not set'
            }, status=500)

        # Try to initialize the LLM caller
        llm_caller = OriginalLLMCaller()
        
        # Try a simple test prompt
        test_prompt = "Say 'Hello, this is a test!'"
        response = llm_caller.call_llm(test_prompt)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Credentials and LLM integration working correctly',
            'test_response': response
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def test_llm(request):
    try:
        # Initialize the LLM caller
        llm_caller = CurlLLMCaller()
        
        # Create a test message
        messages = [
            {"role": "user", "content": "What is the faculty of engineering?"}
        ]
        system_prompt = "You are a chatbot of the faculty of engineering of Thammasat university. Your job is to answer question related to the faculty. Your answer should be short"
        
        # Get response from LLM
        response = llm_caller.generate_response(messages, system_prompt)
        
        return JsonResponse({
            'status': 'success',
            'response': response
        })
    except Exception as e:
        logger.error(f"Error in test_llm view: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

def test_llm_gemini(request):
    try:
        # Initialize the LLM caller
        llm_caller = GeminiLLMCaller()
        
        # Create a test message
        messages = [
            {"role": "user", "content": "What is the faculty of engineering?"}
        ]
        system_prompt = "You are a chatbot of the faculty of engineering of Thammasat university. Your job is to answer question related to the faculty. Your answer should be short"
        
        # Get response from LLM
        response = llm_caller.generate_response(messages, system_prompt)
        
        return JsonResponse({
            'status': 'success',
            'response': response
        })
    except Exception as e:
        logger.error(f"Error in test_llm_gemini view: {e}")
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
