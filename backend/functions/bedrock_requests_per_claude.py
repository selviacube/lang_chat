import boto3
from decouple import config
import json

# Import Custom Functions
from functions.database import get_recent_messages

# Retrieve Environment Variables
aws_access_key_id = config("AWS_ACCESS_KEY_ID")
print("/nAWS_ACCESS_KEY_ID: ", aws_access_key_id)
aws_secret_access_key = config("AWS_SECRET_ACCESS_KEY")
aws_region = config("AWS_REGION")
bedrock_model_id = config("BEDROCK_MODEL_ID")

# AWS Bedrock Client
bedrock_client = boto3.client(
    "bedrock",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region,
)
# Create a Bedrock runtime client
bedrock_runtime = boto3.client("bedrock-runtime", region_name=aws_region)


# Convert Audio to Text using Claude - NOT SUPPORTED
# def convert_audio_to_text_with_bedrock(audio_file):
#     try:
#         response = bedrock_runtime.transcribe_audio(
#             model_id=bedrock_model_id, audio_file=audio_file, language="es"
#         )
#         message_text = response["text"]
#         return message_text
#     except Exception as e:
#         print("Error: ", e)
#         return None


# Get grading evaluation using Claude - MUST THIS BE A SEPARATE FUNCTION?
def get_bedrock_grading_evaluation(message_input, system_prompt):
    messages = get_recent_messages(system_prompt)
    user_message = {"role": "user", "content": message_input}
    messages.append(user_message)
    print("\nget_bedrock: ", messages)
    # temp_message = "Hola, ¿cómo estás?"
    print("\nJSON: ", json.dumps(messages))

    body = json.dumps(
        {
            # "prompt": "\n\nHuman:explain black holes to 8th graders\n\nAssistant:",
            "system": system_prompt,
            "messages": messages,
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 300,
            "temperature": 0.1,
            "top_p": 0.9,
        }
    )

    try:
        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-opus-20240229-v1:0",
            accept="application/json",
            body=body,  # json.dumps(user_message),
        )
        # response_body = json.loads(response.get("body").read())

        result = json.loads(response.get("body").read())
        input_tokens = result["usage"]["input_tokens"]
        output_tokens = result["usage"]["output_tokens"]
        output_list = result.get("content", [])

        print("Invocation details:")
        print(f"- The input length is {input_tokens} tokens.")
        print(f"- The output length is {output_tokens} tokens.")

        print(f"- The model returned {len(output_list)} response(s):")
        print("\nResponse from Bedrock: ", output_list)
        for output in output_list:
            print(output["text"])

        # print("\nResponse from Bedrock: ", response_body.get("completion"))
        # message_text = response["choices"][0]["message"]["content"]
        # return message_text
        return output_list[0]["text"]
    except Exception as e:
        print("Error: ", e)
        return None


# Get response to our message using Claude
def get_bedrock_chat_response(message_input, system_prompt):
    messages = get_recent_messages(system_prompt)
    print("\nget_bedrock | messages array: ", messages)
    user_message = {"role": "user", "content": message_input}
    messages.append(user_message)
    print("\nget_bedrock: ", messages)
    # temp_message = "Hola, ¿cómo estás?"
    print("\nJSON: ", json.dumps(messages))

    body = json.dumps(
        {
            # "prompt": "\n\nHuman:explain black holes to 8th graders\n\nAssistant:",
            "system": system_prompt,
            "messages": messages,
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 2000,
            "temperature": 0.1,
            "top_p": 0.9,
        }
    )

    try:
        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-opus-20240229-v1:0",
            accept="application/json",
            body=body,  # json.dumps(user_message),
        )
        # response_body = json.loads(response.get("body").read())

        result = json.loads(response.get("body").read())
        input_tokens = result["usage"]["input_tokens"]
        output_tokens = result["usage"]["output_tokens"]
        output_list = result.get("content", [])

        print("Invocation details:")
        print(f"- The input length is {input_tokens} tokens.")
        print(f"- The output length is {output_tokens} tokens.")

        print(f"- The model returned {len(output_list)} response(s):")
        print("\nResponse from Bedrock: ", output_list)
        for output in output_list:
            print(output["text"])

        # print("\nResponse from Bedrock: ", response_body.get("completion"))
        # message_text = response["choices"][0]["message"]["content"]
        # return message_text
        return output_list[0]["text"]
    except Exception as e:
        print("Error: ", e)
        return None
