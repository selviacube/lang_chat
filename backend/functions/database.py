import json
import random


# Get recent messagea
def get_recent_messages(system_prompt):
    # Define the file name and learn instruction
    file_name = "stored_data.json"

    learn_instruction = {
        "role": "system",
        "content": system_prompt,
    }

    # Initialize message
    messages = []

    # Get last messages
    try:
        with open(file_name) as user_file:
            data = json.load(user_file)
            # if data:
            #     if len(data) < 5:
            #         for item in data:
            #             messages.append(item)
            #     else:
            #         for item in data[-5:]:
            #             messages.append(item)
            for item in data:
                messages.append(item)
    except Exception as e:
        print("Error: ", e)
        pass

    return messages


# Store messages
def store_messages(request_message, response_message, system_prompt):
    # Define the file name
    file_name = "stored_data.json"

    # Get recent messages
    messages = get_recent_messages(system_prompt)
    user_message = {"role": "user", "content": request_message}
    assistant_message = {"role": "assistant", "content": response_message}
    messages.append(user_message)
    messages.append(assistant_message)

    with open(file_name, "w") as f:
        json.dump(messages, f)


# Reset message history to empty list by writing an empty file on stored_data.json
def reset_messages():
    messages = []  # get_recent_messages("")
    with open("stored_data.json", "w") as f:
        json.dump(messages, f)
        f.close()
        print("Conversation file cleared.")


# def reset_messages():
#     open("stored_data.json", "w")
