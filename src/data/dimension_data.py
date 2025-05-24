import os
import json
import discord
from src.data.const import DIMENSION_PATH

def edit_instruction(interaction: discord.Interaction, message: str):
    channel = interaction.channel
    if isinstance(channel, discord.DMChannel):
        data = createOrFetchChannelConfig("dm",interaction.user.name)
    else:    
        data = createOrFetchChannelConfig(channel.guild.name,channel.name)
    data["instruction"] =  message
    replaceJsonContent(interaction.channel.guild.name, interaction.channel.name,data)
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
    data["globalvar"] =  message
    replaceJsonContent(interaction.channel.guild.name,interaction.channel.name,data)
    return data["globalvar"]

def get_global(interaction: discord.Interaction):
    channel = interaction.channel
    if isinstance(channel, discord.DMChannel):
        data = createOrFetchChannelConfig("dm",interaction.user.name)
    else:    
        data = createOrFetchChannelConfig(channel.guild.name,channel.name)
    return data["globalvar"]

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
        replaceJsonContent(interaction.guild.name,interaction.channel.name,data)
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
    replaceJsonContent(interaction.guild.name,interaction.channel.name, data)
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
    replaceJsonContent(interaction.guild.name,interaction.channel.name, data)

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
        replaceJsonContent(interaction.guild.name,interaction.channel.name, data)
    
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

def replaceJsonContent(location, file_name, new_content):
    """Replaces the content of the JSON file with a given dictionary."""
    # Ensure the file name ends with .json
    if not file_name.endswith(".json"):
        file_name += ".json"
    
    # Check if the file exists
    if not os.path.exists(f"{DIMENSION_PATH}/{location}/{file_name}"):
        print(f"File '{file_name}' does not exist. Cannot replace content.")
        return None

    # Ensure new_content is a dictionary
    if not isinstance(new_content, dict):
        raise ValueError("New content must be a dictionary.")

    # Replace the content
    with open(f"{DIMENSION_PATH}/{location}/{file_name}", "w") as json_file:
        json.dump(new_content, json_file, indent=4)
    print(f"File '{file_name}' content replaced with: {new_content}")
    return new_content


async def get_channel_whitelist(server_name:str,channel_name: str) -> list[str] | None: # This needs server  too
    file_path = f"{DIMENSION_PATH}/{server_name}/{channel_name}.json"

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
    
def init_channel(server,channel):
    createOrFetchChannelConfig(server,channel)
    return

def createOrFetchChannelConfig(server, channel):
    # File name with .json extension
    directory = f"{DIMENSION_PATH}/{server}"
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
        "whitelist": ["Viel"]
    }
    with open(file_name, "w") as json_file:
        json.dump(data, json_file, indent=4)
    print(f"File '{file_name}' created with content: {data}")
    return data
