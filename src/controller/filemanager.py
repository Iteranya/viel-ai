import json
from typing import Any
import discord
import os
import re

async def get_bot_list() -> list[str]:
    names = []
    folder_path = "./characters"
    # Iterate over each file in the directory
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith('.json'):
            # Read the JSON file
            with open(file_path, 'r') as f:
                try:
                    # Load JSON data
                    data = json.load(f)
                    # Extract the name field and append to names list
                    card_data = data.get('data')
                    name  = data.get('name')
                    if name:
                        names.append(name)
                    elif card_data:
                        name = card_data.get("name")
                        if name:
                            names.append(name)
                        else:
                            pass
                    else:
                        pass
                except json.JSONDecodeError as e:
                    print(f"Error parsing {filename}: {e}")

    return names

async def get_channel_whitelist(channel_name: str) -> list[str] | None:
    file_path = f"./channels/{channel_name}.json"

    # Check if the file exists
    if not os.path.exists(file_path):
        return None

    # Attempt to read and parse the JSON file
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            # Extract the 'whitelist' field, if present
            return data.get('whitelist', None)
    except json.JSONDecodeError as e:
        print(f"Error parsing {channel_name}: {e}")

    return None

def get_json_file(filename: str) -> dict[str, Any] | None:
    # Try to go read the file!
    try:
        with open(filename, 'r') as file:
            contents = json.load(file)
            return contents
    # Be very sad if the file isn't there to read
    except FileNotFoundError:
        # await write_to_log("File " + filename + "not found. Where did you lose it?")
        return None
    # Be also sad if the file isn't a JSON or is malformed somehow
    except json.JSONDecodeError:
        # await write_to_log("Unable to parse " + filename + " as JSON.")
        return None
    # Be super sad if we have no idea what's going on here
    except Exception as e:
        #await write_to_log(f"An unexpected error occurred: {e}")
        return None
    
def init_channel(server,channel):
    createOrFetchChannelConfig(server,channel)
    return

def createOrFetchChannelConfig(server,channel):
    # File name with .json extension
    file_name = f"channels/{server}/{channel}.json"

    # Check if the file already exists
    if os.path.exists(file_name):
        # Open and fetch the content
        with open(file_name, "r") as json_file:
            data = json.load(json_file)
        print(f"File '{file_name}' already exists. Fetched content: {data}")
        return data
    
    # If it doesn't exist, create the data and save it
    data = {
        "name": channel,
        "description":"[System Note: Takes place in a discord text channel]",
        "global":"[System Note: Takes place in a discord server]",
        "instruction":"[System Note: Takes place in a discord text channel]"
        }
    with open(file_name, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"File '{file_name}' created with content: {data}")
    return data

def createOrFetchJson(input_string):
    # File name with .json extension
    file_name = f"channels/{input_string}.json"

    # Check if the file already exists
    if os.path.exists(file_name):
        # Open and fetch the content
        with open(file_name, "r") as json_file:
            data = json.load(json_file)
        print(f"File '{file_name}' already exists. Fetched content: {data}")
        return data
    
    # If it doesn't exist, create the data and save it
    data = {
        "name": input_string,
        "description":"[System Note: Takes place in a discord text channel]",
        "global":"[System Note: Takes place in a discord server]",
        "instruction":"[System Note: Takes place in a discord text channel]"
        }
    with open(file_name, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"File '{file_name}' created with content: {data}")
    return data

def replaceJsonContent(file_name, new_content):
    """Replaces the content of the JSON file with a given dictionary."""
    # Ensure the file name ends with .json
    if not file_name.endswith(".json"):
        file_name += ".json"
    
    # Check if the file exists
    if not os.path.exists("channels/"+file_name):
        print(f"File '{file_name}' does not exist. Cannot replace content.")
        return None

    # Ensure new_content is a dictionary
    if not isinstance(new_content, dict):
        raise ValueError("New content must be a dictionary.")

    # Replace the content
    with open("channels/"+file_name, "w") as json_file:
        json.dump(new_content, json_file, indent=4)
    print(f"File '{file_name}' content replaced with: {new_content}")
    return new_content

def sanitize_string(input_string):

    sanitized_string = re.sub(r'[^\x00-\x7F]+', '', input_string)
    # Remove unwanted symbols (keeping letters, numbers, spaces, and basic punctuation)
    sanitized_string = re.sub(r'[^a-zA-Z0-9\s.,!?\'\"-]', '', sanitized_string)
    return sanitized_string.strip()


