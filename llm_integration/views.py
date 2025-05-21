from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from .llm_caller_3 import LLMCaller as GeminiLLMCaller
import logging

logger = logging.getLogger(__name__)

# Create your views here.

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
