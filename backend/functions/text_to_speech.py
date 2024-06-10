import requests
from decouple import config
import os

ELEVEN_LABS_API_KEY = config("ELEVEN_LABS_API_KEY")
ACTIVE_VOICE = config("ACTIVE_VOICE")


# Eleven Labs
# Convert text to speech
def convert_text_to_speech(message):
    # Define data (body)
    body = {
        "text": message,
        "voice_settings": {
            "stability": 0,
            "similarity_boost": 0,
        },
    }

    # Define voice
    voice_rachel = "21m00Tcm4TlvDq8ikWAM"
    voice_matilda = "6kUFfazO0GGrAXLWTerV"
    voice_maria = "5K2SjAdgoClKG1acJ17G"
    # active_voice = voice_maria

    # Constructing endpoint and headers
    headers = {
        "xi-api-key": ELEVEN_LABS_API_KEY,
        "Content-Type": "application/json",
        "accept": "audio/mpeg",
    }
    endpoint = f"https://api.elevenlabs.io/v1/text-to-speech/{ACTIVE_VOICE}"

    # Send Request
    try:
        response = requests.post(endpoint, json=body, headers=headers)
    except Exceptions as e:
        return

    # Handle Response
    if response.status_code == 200:
        return response.content
    else:
        return
