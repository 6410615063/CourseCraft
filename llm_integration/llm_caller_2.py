# is working. use claude 3 haiku
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
            
            url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/us-central1/publishers/anthropic/models/claude-3-haiku@20240307:streamRawPredict"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            data = {
                "anthropic_version": "vertex-2023-10-16",
                "system": system_prompt,
                "messages": messages,
                "max_tokens": 300,
                "stream": True
            }

            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                return self._convert_response(response)
                # return response.text
            else:
                error_msg = f"API call failed with status {response.status_code}: {response.text}"
                logger.error(error_msg)
                raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"Error in API call: {e}")
            raise

    
# # response -> message
# def convert(response) :
#     response_string = response.text
#     response_list = response_string.split("\n\n")
#     response_msg_list = []
#     for response in response_list :
#         #split 'event' and 'data'
#         response_headers = response.split("\n")
#         event_header = response_headers[0]
#         event = event_header.removeprefix("event: ")
#         if event == "content_block_delta" :
#             data_header = response_headers[1]
#             data = data_header.removeprefix("data: ") #is a json string
#             data_json = json.loads(data)
#             text = data_json['delta']['text']
#             response_msg_list.append(text)

#     response_message = "".join(response_msg_list)
#     return response_message

    def _convert_response(self, response) -> str:
        """Convert streaming response to text."""
        response_string = response.text
        response_list = response_string.split("\n\n")
        response_msg_list = []
        for response in response_list :
            #split 'event' and 'data'
            response_headers = response.split("\n")
            event_header = response_headers[0]
            event = event_header.removeprefix("event: ")
            if event == "content_block_delta" :
                data_header = response_headers[1]
                data = data_header.removeprefix("data: ") #is a json string
                data_json = json.loads(data)
                text = data_json['delta']['text']
                response_msg_list.append(text)

        response_message = "".join(response_msg_list)
        return response_message

    # def _convert_response(self, response) -> str:
    #     """Convert streaming response to text."""
    #     try:
    #         # Process streaming response
    #         full_text = ""
    #         for line in response.iter_lines():
    #             if line:
    #                 # Parse each line of the streaming response
    #                 try:
    #                     # Remove the 'data: ' prefix if present
    #                     line_text = line.decode('utf-8')
    #                     if line_text.startswith('data: '):
    #                         line_text = line_text[6:]  # Remove 'data: ' prefix
                        
    #                     data = json.loads(line_text)
    #                     # The response structure from Vertex AI
    #                     if 'predictions' in data and len(data['predictions']) > 0:
    #                         prediction = data['predictions'][0]
    #                         if 'candidates' in prediction and len(prediction['candidates']) > 0:
    #                             candidate = prediction['candidates'][0]
    #                             if 'content' in candidate:
    #                                 full_text += candidate['content']
    #                 except json.JSONDecodeError:
    #                     continue
    #         return full_text
    #     except Exception as e:
    #         logger.error(f"Error converting response: {e}")
    #         raise

    def generate_response(self, messages: List[Dict[str, str]], system_prompt: str) -> str:
        """Generate response from LLM."""
        try:
            return self._make_api_call(messages, system_prompt)
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
