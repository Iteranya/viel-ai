import base64
import requests
import json
from src.data.config_data import get_key
from openai import OpenAI
import os
async def describe_image_koboldcpp(image_path: str, prompt: str = "Write a descriptive caption for this image") -> str:
    try:
        print("Nya?")

        # Encode image as base64
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")

        # Build request payload
        payload = {
            "max_context_length": 16000,
            "max_length": 1024,
            "images": [img_b64],
            "prompt": f"User:{prompt} .\n\nAssistant: ",
            "quiet": False,
            "rep_pen": 1.1,
            "rep_pen_range": 256,
            "rep_pen_slope": 1,
            "temperature": 0.5,
            "tfs": 1,
            "top_a": 0,
            "top_k": 100,
            "top_p": 0.9,
            "typical": 1,
        }

        # Send POST request to your local server
        resp = requests.post("http://localhost:5001/api/v1/generate", json=payload)

        # Debugging output
        print("Humu")
        print("Status:", resp.status_code)
        print("Raw response:", resp.text)
        print(resp)

        # If server returns JSON with a text field
        try:
            result = resp.json()
            return result.get("text", str(result))
        except json.JSONDecodeError:
            return resp.text

    except Exception as e:
        print(e)
        return f"Error: {e}"



# Initialize client


async def describe_image(image_path: str) -> str:
    """
    Takes an image file path, sends it to OpenAI Vision,
    and returns a description of the image.
    """
    import base64
    from openai import OpenAI

    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=get_key(),
    )

    try:
        response = client.chat.completions.create(
            model="moonshotai/kimi-vl-a3b-thinking:free", 
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Write a descriptive caption for this image."},
                        {"type": "image_url", "image_url": f"data:image/png;base64,{img_b64}"},
                    ],
                }
            ],
        )

        # ✅ Access correctly
        print(response)
        return response.choices[0].message.content[0]

    except Exception as e:
        return f"Error: {e}"

def describe_image_hf(image_path: str) -> str:
    API_URL = " https://huggingface.co/api/models/MiaoshouAI/Florence-2-base-PromptGen-v2.0"
    API_TOKEN = os.getenv("HF_API_TOKEN")  # put your token in an env var

    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    # Open image as binary
    with open(image_path, "rb") as f:
        files = {"file": f}
        data = {"inputs": "<MORE_DETAILED_CAPTION>"}
        response = requests.post(API_URL, headers=headers, data=data, files=files)

    if response.status_code != 200:
        raise RuntimeError(f"Request failed: {response.status_code} - {response.text}")

    return response.json()


# Example usage
print(describe_image_hf("Herta.png"))
