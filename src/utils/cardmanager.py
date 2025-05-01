from PIL import Image,PngImagePlugin

import base64
import json
import os
from typing import Dict, Any

def extract_json_from_png(image_path: str) -> Dict[str, Any]:
    """
    Extract JSON metadata from a PNG image's tEXt chunk.

    Args:
        image_path (str): Path to the PNG image file

    Returns:
        Dict[str, Any]: Parsed JSON data from the image

    Raises:
        ValueError: If no JSON metadata is found or parsing fails
    """
    # Predefined key for the text chunk
    TEXT_KEY = "Chara"

    # Open the image
    with Image.open(image_path) as img:
        # Ensure the image is a PNG
        if not isinstance(img, PngImagePlugin.PngImageFile):
            print("The provided file is not a valid PNG image.")

        # Access metadata (tEXt/iTXt chunks)
        metadata = img.info

        # Check if the specific text chunk exists
        if TEXT_KEY not in metadata:
            print(f"No '{TEXT_KEY}' entry found in PNG metadata.")

        # Decode the base64 encoded text
        try:
            decoded_text = base64.b64decode(metadata[TEXT_KEY])
        except Exception as e:
            print(f"Failed to decode base64 text: {e}")

        # Verify it looks like a JSON object
        if not decoded_text.startswith(b'{'):
            print("Decoded metadata does not appear to be a JSON object.")

        # Parse the JSON
        try:
            json_data = json.loads(decoded_text)
            return json_data
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")

def png_to_json(image_path: str):
    """
    Extract JSON from a PNG and save it as a JSON file.

    Args:
        image_path (str): Path to the PNG image file
    
    Returns:
        str: Path to the generated JSON file
    """
    print("Extract JSON from the image")
    json_data = extract_json_from_png(image_path)
    print(str(json_data))

    # Generate JSON output path (same as image path, but with .json extension)
    json_path = os.path.splitext(image_path)[0] + '.json'

    # Write JSON to file
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2)

    return json_path
