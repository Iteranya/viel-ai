import requests
import base64
from src.data.config_data import get_key
import requests

async def invoke_chute(prompt):
    key = get_key()
    if not key.startswith("cpk_"):
        return
    
    headers = {
        "Authorization": f"Bearer {get_key()}",
        "Content-Type": "application/json"
    }

    body = {
        "seed": None,
        "shift": 3,
        "prompt": prompt,
        "resolution": "1024x1024",
        "negative_prompt": "blur, distortion, low quality",
        "guidance_scale": 7.5,
        "width": 1024,
        "height": 1024,
        "num_inference_steps": 50
    }

    response = requests.post(
        "https://chutes-animepasteldream.chutes.ai/generate",
        headers=headers,
        json=body
    )

    print(f"Status code: {response.status_code}")
    content_type = response.headers.get("Content-Type", "")

    if "application/json" in content_type:
        try:
            data = response.json()
            print("JSON response:", data)
        except Exception as e:
            print("Failed to parse JSON:", e)
            print("Raw text response:", response.text)

    elif "image/" in content_type:
        # Save raw image bytes
        with open("temp.jpg", "wb") as f:
            f.write(response.content)
        print("Image saved as temp.jpg")

    else:
        print("Unknown response content type:", content_type)
        print("Raw response text:\n", response.text)