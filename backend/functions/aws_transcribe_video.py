import boto3
import os
import time
from botocore.exceptions import BotoCoreError, ClientError
from decouple import config
import requests

# Retrieve AWS credentials and other configuration values
aws_access_key_id = config("AWS_ACCESS_KEY_ID")
aws_secret_access_key = config("AWS_SECRET_ACCESS_KEY")
aws_region_name = config("AWS_REGION_NAME", default="us-west-2")
s3_bucket_name = config("S3_BUCKET_NAME")

# Initialize the Transcribe and S3 clients
s3_client = boto3.client(
    "s3",
    region_name=aws_region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)
transcribe_client = boto3.client(
    "transcribe",
    region_name=aws_region_name,
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
)


def upload_file_to_s3(file_path, bucket_name, object_key):
    try:
        s3_client.upload_file(file_path, bucket_name, object_key)
        return f"s3://{bucket_name}/{object_key}"
    except (BotoCoreError, ClientError) as e:
        print(f"Error uploading to S3: {e}")
        return None


def convert_audio_to_text(audio_file_path, job_name):
    # Upload audio file to S3
    audio_file_key = os.path.basename(audio_file_path)
    audio_file_uri = upload_file_to_s3(audio_file_path, s3_bucket_name, audio_file_key)

    if not audio_file_uri:
        print("Error: Could not upload audio file to S3.")
        return

    # Start transcription job
    try:
        transcribe_client.start_transcription_job(
            TranscriptionJobName=job_name,
            Media={"MediaFileUri": audio_file_uri},
            MediaFormat=audio_file_path.split(".")[-1],  # e.g., 'mp3', 'wav'
            LanguageCode="es-ES",
        )
    except (BotoCoreError, ClientError) as e:
        print(f"Error starting transcription job: {e}")
        return

    # Wait for transcription to complete
    while True:
        try:
            status = transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )
            if status["TranscriptionJob"]["TranscriptionJobStatus"] in [
                "COMPLETED",
                "FAILED",
            ]:
                break
            print("Transcription job is still in progress...")
            time.sleep(5)
        except (BotoCoreError, ClientError) as e:
            print(f"Error fetching transcription job status: {e}")
            return

    # if status["TranscriptionJob"]["TranscriptionJobStatus"] == "COMPLETED":
    #     transcript_uri = status["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
    #     # Download and return the transcribed text
    #     try:
    #         transcript_response = s3_client.get_object(
    #             Bucket=s3_bucket_name, Key=audio_file_key
    #         )
    #         transcript_content = transcript_response["Body"].read().decode("utf-8")
    #         return transcript_content
    #     except (BotoCoreError, ClientError) as e:
    #         print(f"Error retrieving transcription: {e}")
    #         return None
    # else:
    #     print("Transcription job failed.")
    #     return None

    if status["TranscriptionJob"]["TranscriptionJobStatus"] == "COMPLETED":
        transcript_uri = status["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]

        try:
            # Retrieve the JSON transcript from the URL provided by Transcribe
            response = requests.get(transcript_uri)
            response.raise_for_status()  # Raise an error if the request was unsuccessful
            transcript_json = response.json()

            # Extract the transcript text
            transcript_content = transcript_json["results"]["transcripts"][0][
                "transcript"
            ]
            return transcript_content

        except (requests.RequestException, KeyError) as e:
            print(f"Error retrieving transcription: {e}")
            return None
    else:
        print("Transcription job failed.")
        return None


# Example usage
# text = transcribe_audio("path/to/your/audio/file.mp3", "unique_transcription_job_name")
