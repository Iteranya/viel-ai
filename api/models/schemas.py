# models/schemas.py
"""Pydantic models for request/response validation."""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any

class CharacterModel(BaseModel):
    name: str = Field(..., description="Name of the character")
    persona: str = Field(..., description="Character persona description")
    examples: List[str] = Field(default_factory=list, description="Example interactions")
    instructions: str = Field("", description="Special instructions for the character")
    avatar: str = Field("", description="URL or path to avatar image")
    info: str = Field("", description="Additional info about the character")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Character1",
                "persona": "A helpful assistant",
                "examples": ["User: How are you? Character: I'm doing great!"],
                "instructions": "Always be polite and helpful",
                "avatar": "/images/char1.png",
                "info": "Created on May 6, 2025"
            }
        }

class ChannelModel(BaseModel):
    name: str = Field(..., description="Channel name")
    instruction: str = Field("", description="Channel instructions")
    globalvar: str = Field("", description="Global variables")
    location: str = Field("", description="Location description")
    lorebook: Dict[str, Any] = Field(default_factory=dict, description="Lorebook entries")
    whitelist: List[str] = Field(default_factory=list, description="Whitelist interaction")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "general",
                "instruction": "This is a general chat channel",
                "globalvar": "game_started=true",
                "location": "Main hub",
                "lorebook": {
                    "entry1": "Important lore information"
                },
                "whitelist":["Vida-chan Viel"]
            }
        }

class BotConfigModel(BaseModel):
    default_character: str = Field("Viel", description="Default character name")
    ai_endpoint: str = Field("https://generativelanguage.googleapis.com/v1beta/openai/", 
                           description="AI API endpoint")
    base_llm: str = Field("gemini-2.5-pro-exp-03-25", description="Base LLM model name")
    temperature: float = Field(0.5, description="Temperature setting for AI generation")
    ai_key: str = Field("", description="AI API key")
    discord_key: str = Field("", description="Discord API key")
    
    class Config:
        schema_extra = {
            "example": {
                "default_character": "Viel",
                "ai_endpoint": "https://generativelanguage.googleapis.com/v1beta/openai/",
                "base_llm": "gemini-2.5-pro-exp-03-25",
                "temperature": 0.7,
                "ai_key": "your-api-key",
                "discord_key": "your-discord-key"
            }
        }

class PatchOperation(BaseModel):
    op: str = Field(..., description="Operation type (replace, add, remove)")
    path: str = Field(..., description="JSON path to operate on")
    value: Optional[Any] = Field(None, description="Value for operation (not needed for 'remove')")