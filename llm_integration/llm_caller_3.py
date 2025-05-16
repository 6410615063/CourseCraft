# is working. use gemini 2.0 flash
from google.oauth2 import service_account
import requests
import google.auth.transport.requests
import json
from django.conf import settings
from pathlib import Path
import time
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class LLMCaller:
    def __init__(self):
        self.service_account_name = "service_account_key.json"
        self.service_account_file = Path(settings.BASE_DIR, f"{self.service_account_name}")
        self.project_id = self._get_project_id()
        self.credentials = self._get_credentials()
        self.request = google.auth.transport.requests.Request()
        self.last_call_time = 0
        self.min_interval = 1  # Minimum time between API calls in seconds
        self.model_id = "gemini-2.0-flash-001"

    def _get_project_id(self) -> str:
        """Get project ID from service account file."""
        try:
            with open(self.service_account_file, "r") as file:
                service_account_data = json.load(file)
                return service_account_data["project_id"]
        except Exception as e:
            logger.error(f"Error reading service account file: {e}")
            raise

    def _get_credentials(self) -> service_account.Credentials:
        """Get credentials with required scopes."""
        try:
            scopes = ["https://www.googleapis.com/auth/cloud-platform"]
            return service_account.Credentials.from_service_account_file(
                self.service_account_file, 
                scopes=scopes
            )
        except Exception as e:
            logger.error(f"Error getting credentials: {e}")
            raise

    def _get_access_token(self) -> str:
        """Get fresh access token."""
        try:
            self.credentials.refresh(self.request)
            return self.credentials.token
        except Exception as e:
            logger.error(f"Error refreshing credentials: {e}")
            raise

    def _rate_limit(self):
        """Implement rate limiting between API calls."""
        current_time = time.time()
        time_since_last_call = current_time - self.last_call_time
        if time_since_last_call < self.min_interval:
            time.sleep(self.min_interval - time_since_last_call)
        self.last_call_time = time.time()

    def _make_api_call(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        """Make API call to Google Cloud Vertex AI."""
        try:
            self._rate_limit()
            access_token = self._get_access_token()
            
            # Updated endpoint for Gemini
            url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/us-central1/publishers/google/models/{self.model_id}:generateContent"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            # Convert messages to Gemini format
            contents = []
            for msg in messages:
                contents.append({
                    "role": msg["role"],
                    "parts": [{"text": msg["content"]}]
                })

            data = {
                "contents": contents,
                "generation_config": {
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 1000,
                },
                "systemInstruction": {
                    "role": "",
                    "parts": [
                    {
                        "text": system_prompt
                    }
                    ]
                }
            }

            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                response_text = self._convert_response(response)

                # print(f"_make_api_call: response_text = {response_text}")
                print("_make_api_call: success")

                return response_text
            else:
                error_msg = f"API call failed with status {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"Error in API call: {e}")
            raise

    def _convert_response(self, response) -> str:
        """Convert response to text."""
        try:
            response_data = response.json()
            if 'candidates' in response_data and len(response_data['candidates']) > 0:
                candidate = response_data['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    parts = candidate['content']['parts']
                    return ''.join(part.get('text', '') for part in parts)
            return ""
        except Exception as e:
            logger.error(f"Error converting response: {e}")
            raise

    def generate_response(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        """Generate response from LLM."""
        try:
            return self._make_api_call(messages, system_prompt)
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
