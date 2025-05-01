import json
import re
from aiohttp import ClientSession
from aiohttp import ClientTimeout
from aiohttp import TCPConnector

from aiohttp import ClientSession
from aiohttp import ClientTimeout
from aiohttp import TCPConnector
import random
from typing import Any, Dict
import util
import src.textutil as textutil
from src.models import QueueItem
from src.discordo import Discordo
from src.aicharacter import AICharacter
from src.dimension import Dimension
from src.prompts import PromptEngineer
import config
import aiohttp

class ConfigManager:
    """Class to manage loading configuration from JSON files"""
    
    @staticmethod
    def load_config(filepath: str) -> Dict[str, Any]:
        """Load configuration from a JSON file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in configuration file: {filepath}")

class LlmApi:
    def __init__(self, queue: "QueueItem", prompt_engineer: "PromptEngineer", 
                 config_path: str = "config/llm_config.json", inline=True):
        self.queue = queue
        self.prompt_engineer = prompt_engineer
        self.inline_comprehension = inline
        self.bot = prompt_engineer.bot.bot_name
        
        # Load configuration from JSON file
        self.config = ConfigManager.load_config(config_path)
        
        # Initialize configuration based on model type
        self.model_type = prompt_engineer.type  # Store the model type
        self._initialize_config()

    def _initialize_config(self):
        """Initialize API configuration based on model type"""
        if self.model_type == "local":
            if "local_api" not in self.config:
                raise ValueError("Local API configuration missing in config file")
            self.text_api = self.config["local_api"]
        elif self.model_type == "remote":
            if "remote_api" not in self.config:
                raise ValueError("Remote API configuration missing in config file")
            self.remote_config = self.config["remote_api"]
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")

    async def send_to_model_queue(self) -> "QueueItem":
        timeout = ClientTimeout(total=self.config.get("timeout", 600))
        connector = TCPConnector(limit_per_host=self.config.get("connection_limit", 10))
        async with ClientSession(timeout=timeout, connector=connector) as session:
            try:
                if self.model_type == "local":
                    try:
                        return await self.send_local()
                    except Exception as e:
                        print(f"Something Went Wrong with Local, {e}, using Remote:")
                        return await self.send_remote()
                elif self.model_type == "remote":
                    try:
                        return await self.send_remote()
                    except Exception as e:
                        print(f"API Error: {e}")
                        return await self.handle_error_response(e)
                else:
                    raise ValueError(f"Unsupported model type: {self.model_type}")
            except Exception as e:
                return await self.handle_error_response(e)

    async def handle_error_response(self, e: Exception) -> "QueueItem":
        self.queue.error = "Bot's asleep, probably~ \nHere's the error code:" + str(e)
        return self.queue

    def clean_up(self, llm_response: dict[str, Any]) -> str:
        try:
            data = llm_response['results'][0]['text']
        except KeyError:
            try:
                data = llm_response['choices'][0]['message']['content']
            except KeyError:
                return ""  # Return empty string if no data found.

        if not data:
            return ""

        cleaned_data: str = textutil.remove_last_word_before_final_colon(data)
        cleaned_data = textutil.remove_string_before_final(cleaned_data)
        cleaned_data = cleaned_data.strip()
        if cleaned_data.endswith("*.") or cleaned_data.endswith("*"):
            if random.choice([True, False]):  # 50/50 chance
                cleaned_data = textutil.remove_fluff(cleaned_data)
        cleaned_data = textutil.clean_text(cleaned_data)
        llm_message = cleaned_data

        return llm_message
    
    async def send_local(self):
        timeout = ClientTimeout(total=self.config.get("timeout", 600))
        connector = TCPConnector(limit_per_host=self.config.get("connection_limit", 10))
        async with ClientSession(timeout=timeout, connector=connector) as session:
            if self.model_type == "local":
                url = f"{self.text_api['address']}{self.text_api['generation']}"
                async with session.post(url, 
                                     headers=self.text_api["headers"], 
                                     data=self.queue.prompt) as response:
                    if response.status == 200:
                        try:
                            json_response = await response.json()
                            llm_response: str = self.clean_up(json_response)
                            self.queue.result = llm_response
                            return self.queue
                        except json.decoder.JSONDecodeError as e:
                            return await self.handle_error_response(e)
                    else:
                        print(f"HTTP request failed with status: {response.status}")
                        return await self.handle_error_response(response.status)

    async def send_remote(self):
        model = self.remote_config.get("model")
        api_url = self.remote_config.get("api_url")
        api_key = self.remote_config.get("api_key")
        
        # Prepare messages payload
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": self.queue.prompt,
                }
            ]
        }]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url=api_url,
                    headers={
                        'Accept': 'application/json',
                        'Content-Type': 'application/json',
                        'Authorization': api_key
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "stop": self.prompt_engineer.stopping_string
                    }
                ) as response:
                    # Raise exception for bad HTTP status
                    response.raise_for_status()
                    result = await response.json()
                    print(str(result))
                    if result.get('choices', None) is not None:
                        self.queue.result = result['choices'][0]['message']['content']
                        return self.queue
                    else:
                        self.queue.error = f"Error Occurred: {result['error']['message']}"
                        return self.queue
        except aiohttp.ClientError as e:
            print(f"Network error in LLM evaluation: {e}")
            self.queue.error = f"Error Occurred: {e}"
            return self.queue
        except (KeyError, ValueError) as e:
            print(f"Parsing error in LLM response: {e}")
            self.queue.error = f"Error Occurred: {e}"
            return self.queue            
        except Exception as e:
            print(f"Unexpected error in LLM evaluation: {e}")
            self.queue.error = f"Error Occurred: {e}"
            return self.queue
