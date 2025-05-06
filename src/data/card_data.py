from src.data.const import CHARACTER_PATH
import os
import json
import discord


async def save_character_json(attachment: discord.Attachment) -> str:
    """
    Save a Discord attachment, extracting JSON if it's a PNG with embedded metadata.

    Args:
        attachment (discord.Attachment): The Discord attachment to process

    Returns:
        str: Descriptive string about the processing result
    """
    # Create the attachments directory if it doesn't exist
    attachments_dir = os.path.join(os.getcwd(), CHARACTER_PATH)

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
    

async def get_bot_list() -> list[str]:
    names = []
    folder_path = CHARACTER_PATH
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

