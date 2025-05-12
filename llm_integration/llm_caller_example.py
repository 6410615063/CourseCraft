from google.oauth2 import service_account
import requests
import google.auth.transport.requests
import json
from django.conf import settings
from pathlib import Path

def generate(context) :
    # get service account and project id
    service_account_name = "service_account.json"  # Ensure this path is correct
    service_account_file = Path(settings.BASE_DIR, f"static/{service_account_name}")
    with open(service_account_file, "r") as file:
        service_account_data = json.load(file)
        project_id = service_account_data["project_id"]

    # Define the required scopes
    scopes = ["https://www.googleapis.com/auth/cloud-platform"]

    # Load the service account credentials with the specified scopes
    credentials = service_account.Credentials.from_service_account_file(service_account_file, scopes=scopes)

    # Create a request object
    request = google.auth.transport.requests.Request()

    # Refresh the credentials to get the access token
    credentials.refresh(request)

    # Get the access token
    access_token = credentials.token

    # Plan - make a curl request to vertex api
    url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{project_id}/locations/us-central1/publishers/anthropic/models/claude-3-haiku@20240307:streamRawPredict"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "anthropic_version": "vertex-2023-10-16",
        "system": "You are a chatbot of the faculty of engineering of Thammasat university. Your job is to answer question related to the faculty. Your answer should be short",
        "messages": context,
        "max_tokens": 300,
        "stream": True
    }

    # Make the POST request
    response = requests.post(url, headers=headers, json=data)

    # Check the response status code
    if response.status_code == 200:
        message = convert(response)
        return message
    else:
        print(f"Request failed with status code {response.status_code} and response: {response.text}")
        return "Error happend, check terminal"