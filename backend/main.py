# uvicorn main:app --reload --port ####
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import datetime
import json
import yaml

# from decouple import config
import openai

# Customer Function Imports
from functions.database import store_messages, reset_messages
from functions.openai_requests import get_chat_response, convert_audio_to_text

# from functions.read_yaml import read_yaml

# from functions.aws_transcribe_video import convert_audio_to_text
from functions.text_to_speech_aws_poly import convert_text_to_speech
from functions.bedrock_requests_per_claude import (
    get_bedrock_chat_response,
    get_bedrock_grading_evaluation,
)

# Initiate App
app = FastAPI()

# CORS - Origins
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:4173",
    "http://localhost:4174",
    "http://localhost:3000",
    "http://voicechat.svhs.co",
    "https://voicechat.svhs.co",
]
# CORS - Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def read_yaml(file_path):
    global introduction
    with open(file_path, "r") as file:
        data = yaml.safe_load(file)

        for key, value in data.items():
            globals()[
                key
            ] = value  # Set the variable name to the key and the value to the variable
            print(f"{key}: {value}")
        print("\nIntroduction inside read_yaml: ", introduction)


read_yaml("data/Lang_Chat_Spanish.yaml")
print("\n Introduction from YAML: ", introduction)

system_prompt = ""


def init_system_prompt():
    # global system_prompt
    alternative_system_prompt = ""
    try:
        with open("data/alternative_system_prompt.txt", "r") as file:
            alternative_system_prompt = file.read()
    except:
        pass

    if len(alternative_system_prompt) > 0:
        print("\nUsing alternative system prompt\n")
        print(alternative_system_prompt)
        system_prompt = alternative_system_prompt
    else:
        with open("data/default_system_prompt.txt", "r") as file:
            system_prompt = file.read()
    return system_prompt


system_prompt = init_system_prompt()
print("\nSystem Prompt: \n", system_prompt)
grading_system_prompt = "You are a high school Spanish teacher. You are grading a student's ability to communicate in Spanish."
grading_base_prompt = """
    You are a high school Spanish teacher. Please use the following rubric to grade the student's use of Spanish in the dialog below. Return the result in JSON format only and no other text, with the key "grade" and the value expressed as an integer from 0 to 100 based on the rubric guidelines.
    
    Rubric: Spanish 1, Part1 - Unit 1 Assignment Ready for use
    1.Task Completion
    Student completes a five minute dialogue in which they utilise correctly the appropriate responses. These include different greetings. 
    Maximum score 1-10 (80% of Spanish is correct for maximum score)

    2. Dialogues; Vocabulary
    Student used ample and correct vocabulary/phrases for greetings, introductions, expressions of courtesy and goodbyes.(80% for maximum score of 1-15)
    Maximum score 15

    3. Grammar
    Student used correct grammar,  in the dialogues including the use of the tú and usted forms.( 80% of grammar, is correct for  maximum score of 1-20)
    Maximum score 20

    4.Dialogues; Pronunciation
    Description for students
    Pronunciation is  clear, easy to follow and correct Spanish pronunciation was used.80% of the time for maximum score of 20
    Maximum score 20

    5. Question responses; Grammar and Vocabulary
    Student answers using correct grammar 80% of the time to gain maximum marks of 1-20
    Maximum score 20

    6. Question responses; Pronunciation

    Voice  was clear, easy to follow and correct Spanish pronunciation was used 80% of the time to gain maximum marks of 15

    Maximum score 15

    Student/Teacher dialog:
    """

# # If altnernative system prompt text file exists, read it
# alternative_system_prompt = ""
# try:
#     with open("data/alternative_system_prompt.txt", "r") as file:
#         alternative_system_prompt = file.read()
# except:
#     pass


# # Read default system prompt from file
# def get_default_system_prompt():
#     with open("data/default_system_prompt.txt", "r") as file:
#         return file.read()


# # Set default system prompt
# if len(alternative_system_prompt) > 0:
#     print("\nUsing alternative system prompt\n")
#     print(alternative_system_prompt)
#     system_prompt = alternative_system_prompt
# else:
#     system_prompt = get_default_system_prompt()


@app.get("/health")
async def check_health():
    return {"message": "Healthy"}


# Reset messages
@app.get("/reset")
async def reset_conversation():
    global system_prompt
    system_prompt = init_system_prompt()
    reset_messages()
    return {"message": "conversation reset"}


@app.get("/get-starting-prompt")
async def get_starting_prompt():
    return {"starting_prompt": starting_prompt}


@app.get("/get-introduction")
async def get_introduction():
    global introduction
    return {"introduction": introduction}


@app.get("/get-system-prompt")
async def get_system_prompt():
    return {"system_prompt": system_prompt}


# Store alternative system prompt
class SystemPromptInput(BaseModel):
    system_prompt: str


@app.post("/store-alternative-system-prompt/")
async def store_alternative_system_prompt(input_data: SystemPromptInput):
    if len(input_data.system_prompt) > 10:
        with open("data/alternative_system_prompt.txt", "w") as file:
            file.write(input_data.system_prompt)
    else:
        # Delete alternative system prompt file
        try:
            os.remove("data/alternative_system_prompt.txt")
        except:
            pass
    init_system_prompt()
    return {"message": "Alternative system prompt updated."}


# To get back the text, as well as the audio, I believe I
# need to create three separate end points. The first would convert the
# audio request to text. The second would obtain the
# text response from the LLM. The third would pass that text response
# back to an endpoint to convert it to speech. This requires three endpoints
# because the audio response is streamed in chunks, so it cannot return both
# the audio stream and the text in a single http response.


# Accept binary audio and convert to text.
@app.post("/transcribe-audio/")
async def transcribe_audio(file: UploadFile = File(...)):
    # Save file from frontend
    with open(file.filename, "wb") as buffer:
        buffer.write(file.file.read())
        # Get full path to file
        path_to_audio_file = os.path.abspath(file.filename)

    # AWS CALL:
    # Ideally, the job_name would include a student ID.
    # job_name = "transcription-" + datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    # message_decoded = convert_audio_to_text(path_to_audio_file, job_name)

    # WHISPER CALL:
    audio_input = open(file.filename, "rb")
    message_decoded = convert_audio_to_text(audio_input)

    print(message_decoded)
    if not message_decoded:
        return HTTPException(status_code=400, detail="Audio not decoded.")

    return {"message": message_decoded}


class MessageInput(BaseModel):
    message_input: str


# Get grade response
@app.post("/get-grade-response/")
async def get_grade_response(input_data: MessageInput):
    print("\nMessage Input: ", input_data.message_input)
    # chat_response = get_chat_response(input_data.message_input, system_prompt)
    chat_response = get_bedrock_grading_evaluation(
        grading_base_prompt + input_data.message_input, grading_system_prompt
    )
    if not chat_response:
        return HTTPException(status_code=400, detail="Failed to get chat response.")

    print("\nGrading Response: '" + chat_response + "'")
    print("\nGrading Response Type: ", type(chat_response))

    # store_messages(input_data.message_input, chat_response, system_prompt)
    return json.loads(chat_response)


# Get chat response
@app.post("/get-text-response/")
async def get_text_response(input_data: MessageInput):
    print("\nMessage Input: ", input_data.message_input)
    # chat_response = get_chat_response(input_data.message_input, system_prompt)
    chat_response = get_bedrock_chat_response(input_data.message_input, system_prompt)
    if not chat_response:
        return HTTPException(status_code=400, detail="Failed to get chat response.")

    store_messages(input_data.message_input, chat_response, system_prompt)
    return {"message": chat_response}


# Convert text to speech and return audio data
@app.post("/get-TTS/")
async def get_TTS(input_data: MessageInput):
    audio_output = convert_text_to_speech(input_data.message_input)
    if not audio_output:
        return HTTPException(
            status_code=400, detail="Failed to get Eleven Labs audio response."
        )

    # Create a generator that yields chunks of data
    def iterfile():
        yield audio_output

    # Return audio file
    return StreamingResponse(iterfile(), media_type="application/octet-stream")


# Get audio - DEPRECATED
@app.post("/post-audio/")
async def post_audio(file: UploadFile = File(...)):
    # FOR TESTING:
    #   audio_input = open("SimpleVoiceRecording.mp3", "rb")

    # Save file from frontend
    with open(file.filename, "wb") as buffer:
        buffer.write(file.file.read())
    audio_input = open(file.filename, "rb")

    message_decoded = convert_audio_to_text(audio_input)

    print(message_decoded)
    if not message_decoded:
        return HTTPException(status_code=400, detail="Audio not decoded.")

    # Get chat response
    chat_response = get_chat_response(message_decoded, system_prompt)
    if not chat_response:
        return HTTPException(status_code=400, detail="Failed to get chat response.")

    store_messages(message_decoded, chat_response, system_prompt)
    audio_output = convert_text_to_speech(chat_response)
    if not audio_output:
        return HTTPException(
            status_code=400, detail="Failed to get Eleven Labs audio response."
        )

    # Create a generator that yields chunks of data
    def iterfile():
        yield audio_output

    # Return audio file
    return StreamingResponse(iterfile(), media_type="application/octet-stream")
