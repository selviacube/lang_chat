import boto3
import decouple
from functions.database import get_recent_messages

# Set up AWS client for Bedrock
aws_access_key_id = config("AWS_ACCESS_KEY_ID")
aws_secret_access_key = config("AWS_SECRET_ACCESS_KEY")
aws_region = config("AWS_REGION")

bedrock_client = boto3.client(
    "bedrock",
    aws_access_key_id=aws_access_key_id,
    aws_secret_access_key=aws_secret_access_key,
    region_name=aws_region,
)


# Function to get a response using Claude model from AWS Bedrock
def get_bedrock_chat_response(message_input, system_prompt):
    messages = get_recent_messages(system_prompt)
    user_message = {"role": "user", "content": message_input}
    messages.append(user_message)
    print(messages)

    try:
        response = bedrock_client.chat(
            model="aws-ai-chatbot-claude",  # Use the specific model identifier if different
            messages=messages,
        )
        message_text = response["messages"][-1][
            "content"
        ]  # Adjust based on actual response structure
        return message_text
    except Exception as e:
        print("Error: ", e)
        return


# Example usage
# response_text = get_chat_response("Hello, how are you?", "System prompt goes here")
# print(response_text)
