# is not working
import os
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import google.generativeai as genai
from django.conf import settings

class LLMCaller:
    def __init__(self):
        self.last_call_time = None
        self.min_time_between_calls = 12  # 5 calls per minute = 12 seconds between calls
        self.max_retries = 3
        self.retry_delay = 5  # seconds
        
        # Configure the Gemini API with API key
        if not settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not set in settings")
            
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        # Initialize the model - using Gemini 2.0 Flash
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def _wait_for_rate_limit(self) -> None:
        """Wait if necessary to respect rate limits."""
        if self.last_call_time is not None:
            time_since_last_call = (datetime.now() - self.last_call_time).total_seconds()
            if time_since_last_call < self.min_time_between_calls:
                time.sleep(self.min_time_between_calls - time_since_last_call)
        self.last_call_time = datetime.now()

    def _handle_api_error(self, error: Exception, retry_count: int) -> Optional[Dict[str, Any]]:
        """Handle API errors and implement retry logic."""
        if retry_count < self.max_retries:
            time.sleep(self.retry_delay)
            return None
        raise Exception(f"Failed after {self.max_retries} retries. Last error: {str(error)}")

    def call_llm(self, prompt: str) -> Dict[str, Any]:
        """
        Call the LLM API with rate limiting and error handling.
        
        Args:
            prompt (str): The prompt to send to the LLM
            
        Returns:
            Dict[str, Any]: The LLM response
            
        Raises:
            Exception: If the API call fails after all retries
        """
        retry_count = 0
        while retry_count <= self.max_retries:
            try:
                self._wait_for_rate_limit()
                
                # Call the Gemini API
                response = self.model.generate_content(prompt)
                
                # Process and return the response
                return {
                    'text': response.text,
                    'timestamp': datetime.now().isoformat(),
                    'success': True
                }
                
            except Exception as e:
                retry_count += 1
                result = self._handle_api_error(e, retry_count)
                if result is not None:
                    return result
                
        raise Exception("Failed to get response from LLM after all retries")

    def check_rate_limit(self) -> Dict[str, Any]:
        """
        Check if we're currently rate limited.
        
        Returns:
            Dict[str, Any]: Information about the rate limit status
        """
        if self.last_call_time is None:
            return {
                'rate_limited': False,
                'wait_time': 0
            }
            
        time_since_last_call = (datetime.now() - self.last_call_time).total_seconds()
        if time_since_last_call < self.min_time_between_calls:
            return {
                'rate_limited': True,
                'wait_time': self.min_time_between_calls - time_since_last_call
            }
            
        return {
            'rate_limited': False,
            'wait_time': 0
        } 