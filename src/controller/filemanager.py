import json
from typing import Any
import discord
import os
import re
import aiohttp
from dataclasses import dataclass,asdict

CONFIG_PATH = "configurations/bot_config.json"

@dataclass
class Config:
    system_note: str = "ONLY USE HTML, CSS AND JAVASCRIPT. If you want to use ICON make sure to import the library first. Try to create the best UI possible by using only HTML, CSS and JAVASCRIPT. Also, try to ellaborate as much as you can, to create something unique. ALWAYS GIVE THE RESPONSE INTO A SINGLE HTML FILE"
    ai_endpoint: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    base_llm:str= "gemini-2.5-pro-exp-03-25"
    temperature:float = 0.5
    ai_key:str = ""

async def get_bot_list() -> list[str]:
    names = []
    folder_path = "res/characters"
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

def createOrFetchChannelConfig(server, channel):
    # File name with .json extension
    directory = f"res/servers/{server}"
    file_name = f"{directory}/{channel}.json"
    
    # Create directories if they don't exist
    os.makedirs(directory, exist_ok=True)
    
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
        "instruction":"[System Note: Takes place in a discord text channel]",
        "whitelist": ["Vida-chan"]
    }
    with open(file_name, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"File '{file_name}' created with content: {data}")
    return data

def replaceJsonContent(location, file_name, new_content):
    """Replaces the content of the JSON file with a given dictionary."""
    # Ensure the file name ends with .json
    if not file_name.endswith(".json"):
        file_name += ".json"
    
    # Check if the file exists
    if not os.path.exists(f"{location}/{file_name}.json"):
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

def edit_instruction(interaction: discord.Interaction, message: str):
    channel = interaction.channel
    if isinstance(channel, discord.DMChannel):
        data = createOrFetchChannelConfig("dm",interaction.user.name)
    else:    
        data = createOrFetchChannelConfig(channel.guild.name,channel.name)
    data["instruction"] =  message
    replaceJsonContent(interaction.channel.name,data)
    return data["instruction"]

def get_instruction(interaction: discord.Interaction):
    channel = interaction.channel
    if isinstance(channel, discord.DMChannel):
        data = createOrFetchChannelConfig("dm",interaction.user.name)
    else:    
        data = createOrFetchChannelConfig(channel.guild.name,channel.name)
    return data["instruction"]

def edit_global(interaction: discord.Interaction, message: str):
    channel = interaction.channel
    if isinstance(channel, discord.DMChannel):
        data = createOrFetchChannelConfig("dm",interaction.user.name)
    else:    
        data = createOrFetchChannelConfig(channel.guild.name,channel.name)
    data["global"] =  message
    replaceJsonContent(interaction.channel.name,data)
    return data["global"]

def get_global(interaction: discord.Interaction):
    channel = interaction.channel
    if isinstance(channel, discord.DMChannel):
        data = createOrFetchChannelConfig("dm",interaction.user.name)
    else:    
        data = createOrFetchChannelConfig(channel.guild.name,channel.name)
    return data["global"]

def add_whitelist(interaction: discord.Interaction, character_name: str):
    # Fetch or create the JSON data
    channel = interaction.channel
    if isinstance(channel, discord.DMChannel):
        data = createOrFetchChannelConfig("dm",interaction.user.name)
    else:    
        data = createOrFetchChannelConfig(channel.guild.name,channel.name)

    # Initialize the "whitelist" key if it doesn't exist
    if "whitelist" not in data:
        data["whitelist"] = []

    # Add the character to the whitelist if not already present
    if character_name not in data["whitelist"]:
        data["whitelist"].append(character_name)
        replaceJsonContent(interaction.channel.name,data)
    return data["whitelist"]

def clear_whitelist(interaction: discord.Interaction):
    # Fetch or create the JSON data
    channel = interaction.channel
    if isinstance(channel, discord.DMChannel):
        data = createOrFetchChannelConfig("dm",interaction.user.name)
    else:    
        data = createOrFetchChannelConfig(channel.guild.name,channel.name)

    
    # Clear the whitelist
    data["whitelist"] = []
    replaceJsonContent(interaction.channel.name, data)
    return data["whitelist"]

def set_whitelist(interaction: discord.Interaction, whitelist_string: str):
    # Fetch or create the JSON data
    channel = interaction.channel
    if isinstance(channel, discord.DMChannel):
        data = createOrFetchChannelConfig("dm",interaction.user.name)
    else:    
        data = createOrFetchChannelConfig(channel.guild.name,channel.name)

    # Split the input string by comma and strip whitespace
    new_whitelist_entries = [name.strip() for name in whitelist_string.split(',')]

    # Check if a whitelist already exists; if not, initialize it
    existing_whitelist = data.get("whitelist", [])

    # Combine the existing whitelist with new entries, avoiding duplicates
    combined_whitelist = list(set(existing_whitelist + new_whitelist_entries))

    # Update the whitelist in the data object
    data["whitelist"] = combined_whitelist

    # Save the updated data back to JSON
    replaceJsonContent(interaction.channel.name, data)

    return data["whitelist"]

def delete_whitelist(interaction: discord.Interaction, character_name: str):
    # Fetch or create the JSON data
    channel = interaction.channel
    if isinstance(channel, discord.DMChannel):
        data = createOrFetchChannelConfig("dm",interaction.user.name)
    else:    
        data = createOrFetchChannelConfig(channel.guild.name,channel.name)
    
    # Remove the character from the whitelist if present
    if "whitelist" in data and character_name in data["whitelist"]:
        data["whitelist"].remove(character_name)
        replaceJsonContent(interaction.channel.name, data)
    
    return data["whitelist"]

def get_whitelist(interaction: discord.Interaction):
    # Fetch or create the JSON data
    channel = interaction.channel

    if isinstance(channel, discord.DMChannel):
        data = createOrFetchChannelConfig("dm",interaction.user.name)
    else:    
        data = createOrFetchChannelConfig(channel.guild.name,channel.name)
    
    # Return the whitelist, defaulting to an empty list if not present
    return data.get("whitelist", [])

async def save_character_json(attachment: discord.Attachment) -> str:
    """
    Save a Discord attachment, extracting JSON if it's a PNG with embedded metadata.

    Args:
        attachment (discord.Attachment): The Discord attachment to process

    Returns:
        str: Descriptive string about the processing result
    """
    # Create the attachments directory if it doesn't exist
    attachments_dir = os.path.join(os.getcwd(), 'characters')

    # Generate the base filepath
    filename: str = attachment.filename
    
    # Handle JSON files
    if filename.lower().endswith(".json"):
        filepath = os.path.join(attachments_dir, filename)
        
        # Check if the file already exists
        if os.path.exists(filepath):
            return f"JSON file {filename} already exists"

        # Save the new attachment
        with open(filepath, 'wb') as f:
            attachment_bytes = await attachment.read()
            f.write(attachment_bytes)

        return f"JSON file {filename} saved"
    
async def get_pygmalion_json(uuid:str):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                url=f"https://server.pygmalion.chat/api/export/character/{uuid}/v2",
                headers={
                    "Content-Type": "application/json"
                }
            ) as response:
                # Raise exception for bad HTTP status
                response.raise_for_status()
                result = await response.json()
                print(str(result))
                if result.get('character',None)!=None:
                    try:
                        data = result['character']
                        filename = f"characters/{result['character']['data']['name']}.json"
                        with open(filename, 'w') as file:
                            json.dump(data, file, indent=4)
                        return f"Dictionary successfully saved to {filename}"
                    except Exception as e:
                        print(f"An error occurred: {e}")
                        return print(f"An error occurred: {e}")
                else:
                    return f"Error Reading File: {result['error']['message']}, Notify User That An Error Occured."
    except aiohttp.ClientError as e:
        print(f"Network error in LLM evaluation: {e}")
    except (KeyError, ValueError) as e:
        print(f"Parsing error in LLM response: {e}")
    except Exception as e:
        print(f"Unexpected error in LLM evaluation: {e}")
    return None


def load_or_create_config(path: str = CONFIG_PATH) -> Config:
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
            current_config = Config(**data)
            current_config.ai_key = "" # Duct Tape Security... Fix In Production (Or Not, Maybe This Is Actually Secure Enough :v)
        return current_config
    else:
        default_config = Config()
        save_config(default_config, path)
        print(f"No config found. Created default at {path}.")
        default_config.ai_key = ""
        return default_config
    
def save_config(config: Config, path: str = CONFIG_PATH) -> None:
    with open(path, 'w') as f:
        json.dump(asdict(config), f, indent=2)

def get_key(path:str = CONFIG_PATH) -> str:
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
            current_config = Config(**data)
            return current_config.ai_key 
    else:
        return ""