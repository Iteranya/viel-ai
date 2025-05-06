import requests
import os
from datetime import datetime

def generate_image(prompt, resolution="1024x1024", guidance_scale=5, num_inference_steps=50, shift=3, seed=None):
    """
    Generate an image using the Chutes AI API and save it to the current directory.
    
    Args:
        prompt (str): Text prompt for the image generation
        resolution (str): Image resolution in format "widthxheight"
        guidance_scale (float): Guidance scale for the model
        num_inference_steps (int): Number of inference steps
        shift (int): Shift parameter
        seed (int, optional): Random seed for reproducibility
    
    Returns:
        str: Path to the saved image
    """
    # API configuration
    api_token = "cpk_3db75cb438b64aba8a66c5a7fd0e9231.ade0cdfb680857e4bc8f192cf8869f43.S6uLGf71yyndFEMp9h2si3gE24HIDeA6"  # Replace with your actual API token
    headers = {
        "Authorization": "Bearer " + api_token,
        "Content-Type": "application/json"
    }
    
    # Request body
    body = {
        "seed": seed,
        "shift": shift,
        "prompt": prompt,
        "resolution": resolution,
        "guidance_scale": guidance_scale,
        "num_inference_steps": num_inference_steps
    }
    
    # Make the API request
    print(f"Generating image with prompt: '{prompt}'")
    try:
        response = requests.post(
            "https://chutes-hidream.chutes.ai/generate",
            headers=headers,
            json=body,
            timeout=90  # Extended timeout for image generation
        )
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return None
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Error: Status code {response.status_code}")
        print(f"Response begins with: {response.content[:50]}")
        return None
    
    # Create a timestamped filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chutes_image_{timestamp}.jpg"  # Assuming JPEG format based on the response
    
    # Check the content type header if it exists
    content_type = response.headers.get('Content-Type', '')
    if 'json' in content_type.lower():
        # Handle JSON response (could contain base64 image)
        try:
            response_data = response.json()
            if "image" in response_data:
                # If it's base64 encoded
                import base64
                image_data = base64.b64decode(response_data["image"])
                with open(filename, "wb") as f:
                    f.write(image_data)
                print(f"Image saved as {filename}")
                return filename
            else:
                print("No image data found in JSON response")
                print(response_data)
                return None
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            # Fall through to binary handling
    
    # Handle binary image response (direct image data)
    try:
        # Determine file extension based on content type or signature
        if 'jpeg' in content_type.lower() or 'jpg' in content_type.lower() or response.content[:3] == b'\xff\xd8\xff':
            extension = "jpg"
        elif 'png' in content_type.lower() or response.content[:8] == b'\x89PNG\r\n\x1a\n':
            extension = "png"
        else:
            extension = "img"  # Generic fallback
        
        filename = f"chutes_image_{timestamp}.{extension}"
        
        # Save the raw image data
        with open(filename, "wb") as f:
            f.write(response.content)
        
        print(f"Image saved as {filename}")
        return filename
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Generate an image of a fish
    generate_image(
        prompt="A fish",
        resolution="1024x1024",
        guidance_scale=7,
        num_inference_steps=50
    )