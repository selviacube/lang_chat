import openai
from decouple import config

# Import Custom Functions
from functions.database import get_recent_messages

# Retrieve Environment Variables
openai.organization = config("OPEN_AI_ORG")
openai.api_key = config("OPEN_AI_KEY")


# Open AI - Whisper
# Convert Audio to Text
def convert_audio_to_text(audio_file):
    try:
        transcript = openai.Audio.transcribe(
            "whisper-1",
            audio_file,
            language="es",
            prompt="El hablante sólo sabe español rudimentario y sus expresiones deben interpretarse con la expectativa de un vocabulario y una gramática limitados.",
        )
        # transcript = client.audio.transcriptions.create(
        #     model="whisper-1", file=audio_file, language="es"
        # )
        message_text = transcript["text"]
        return message_text
    except Exception as e:
        print("Error: ", e)
        return


# Open AI - GPT
# Get response to our message
def get_chat_response(message_input, system_prompt):
    messages = get_recent_messages(system_prompt)
    user_message = {"role": "user", "content": message_input}
    messages.append(user_message)
    print(messages)

    try:
        response = openai.ChatCompletion.create(model="gpt-4", messages=messages)
        # print(response)
        message_text = response["choices"][0]["message"]["content"]
        return message_text
    except Exception as e:
        print("Error: ", e)
        return
