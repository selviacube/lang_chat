import boto3
from decouple import config
from dotenv import load_dotenv
import os

AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_REGION = config("AWS_REGION", default="us-west-2")

load_dotenv()


def reload_env():
    load_dotenv(override=True)


# Initialize the Polly client
polly_client = boto3.client(
    "polly",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)


def convert_text_to_speech(message):
    reload_env()
    AWS_POLLY_VOICE_ID = os.getenv("AWS_POLLY_VOICE_ID")
    AWS_POLLY_SPEED = os.getenv("AWS_POLLY_SPEED")
    print("\nAWS_POLLY_SPEED: ", AWS_POLLY_SPEED)
    # Forcing code change
    try:
        response = polly_client.synthesize_speech(
            Text='<speak><prosody rate="'
            + AWS_POLLY_SPEED
            + '">'
            + message
            + "</prosody></speak>",
            OutputFormat="mp3",
            VoiceId=AWS_POLLY_VOICE_ID,  # You can change this to another voice supported by Polly
            TextType="ssml",
        )
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    if response.get("AudioStream"):
        return response["AudioStream"].read()
    else:
        return
