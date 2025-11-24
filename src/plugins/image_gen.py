import aiohttp
from typing import Any, Dict

from api.db.database import Database
from api.models.models import BotConfig
from src.plugins.base import BasePlugin, ActiveCharacter, ActiveChannel


class ImageGenPlugin(BasePlugin):
    triggers = ["image>"]

    async def _generate_image(self, prompt: str, token: str) -> str:
        """Call the ElectronHub Image Generation API."""
        url = "https://api.electronhub.ai/v1/images/generations"

        payload = {
            "model": "flux-dev",
            "prompt": prompt,
            "n": 1,
            "quality": "standard",
            "size": "1024x1024",
            "response_format": "url",
            "public": False
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    print(text)
                    raise RuntimeError(f"Image API Error ({resp.status}): {text}")

                data = await resp.json()
                # Expecting: { "data": [ { "url": "<image_url>" } ] }
                return data["data"][0]["url"]

    async def execute(self, message, character: ActiveCharacter, channel: ActiveChannel, db: Database) -> Dict[str, Any]:
        prompt = (
            message.content
            .replace("image>", "")
            .replace("img>", "")
            .replace("generate_image>", "")
            .strip()
        )

        # However you store API keys — adjust for your setup:
        all_db_configs = db.list_configs()
        # Pydantic will use default values for any keys not found in the DB
        config = BotConfig(**all_db_configs)
        token = config.ai_key
        if not token:
            return {"result": "[No AI Gen Token Provided]"}

        try:
            image_url = await self._generate_image(prompt, token)
        except Exception as e:
            print(e)
            return {"result": f"[System Note: Image generation failed: {e}]"}
        
        return {
            "result": (
                f"[System Note: Image generated for prompt '{prompt}':\n{image_url}]"
            )
        }