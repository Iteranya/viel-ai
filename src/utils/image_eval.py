import base64
import re
import traceback
from openai import AsyncOpenAI

# Adjust these import paths to match your project structure
from api.db.database import Database
from api.models.models import BotConfig

def get_bot_config(db: Database) -> BotConfig:
    """Helper to fetch all config key-values from the DB and return a BotConfig object."""
    all_db_configs = db.list_configs()
    return BotConfig(**all_db_configs)

async def describe_image(image_path: str, db: Database) -> str:
    """
    Takes an image file path, sends it to the configured vision model,
    and returns a description of the image.
    """
    bot_config = get_bot_config(db)

    # 1. Check if the feature is enabled in the config
    if not bot_config.multimodal_enable:
        return "<ERROR> Image description is disabled in the bot's configuration."

    # 2. Check if the required configuration values are set
    if not bot_config.multimodal_ai_endpoint or not bot_config.multimodal_ai_model:
        return "<ERROR> The multimodal endpoint or model is not configured in the bot's settings."

    try:
        with open(image_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode("utf-8")

        # 3. Use the configuration from the database
        client = AsyncOpenAI(
            base_url=bot_config.multimodal_ai_endpoint,
            api_key=bot_config.multimodal_ai_api,  # Use the main AI key
        )

        # 4. Correctly await the asynchronous API call
        response = await client.chat.completions.create(
            model=bot_config.multimodal_ai_model, # Use the configured model
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Write a descriptive caption for this image. If it contains any text or writing, transcribe all of it accurately."},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                    ],
                }
            ],
            max_tokens=1024,
        )

        description = response.choices[0].message.content
        return description if description else "<INFO> The AI returned an empty description for the image."

    except Exception as e:
        print(f"Error describing image: {e}\n{traceback.format_exc()}")
        return f"<ERROR> Image failed to load or process. Check the bot's logs for details."
    

def strip_thinking(text: str) -> str:
    """
    Removes everything before and including the closing think markers:
    - </think>
    - ◁/think▶
    - \u25c1/think\u25b7 (literal unicode escape)
    Returns the cleaned text.
    """
    # Remove everything up to and including any closing think marker
    cleaned = re.sub(r"(?s)^.*?(?:</think>|◁/think▶|◁/think▷|\\u25c1/think\\u25b7)", "", text)
    return cleaned.strip()