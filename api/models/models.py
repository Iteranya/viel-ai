from __future__ import annotations
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

# ------------------------------------------------------
# Config (maps to the 'config' table)
# ------------------------------------------------------

class BotConfig(BaseModel):
    default_character: str
    ai_endpoint: str
    base_llm: str
    temperature: float = 0.7
    auto_cap: int = 2000
    ai_key: str = Field("", description="Can be empty if not needed by the endpoint")
    discord_key: str = Field("", description="Can be empty for testing, but required to run the bot")
    use_prefill: bool = False
    multimodal_enable: bool = False
    multimodal_ai_endpoint: Optional[str] = None
    multimodal_ai_api: Optional[str] = None
    multimodal_ai_model: Optional[str] = None


# ------------------------------------------------------
# Servers (maps to the 'servers' table)
# ------------------------------------------------------
class Server(BaseModel):
    """Represents a single row in the 'servers' table."""
    server_id: str
    server_name: str
    description: Optional[str] = None
    instruction: Optional[str] = None


# ------------------------------------------------------
# Channels (maps to the 'channels' table)
# ------------------------------------------------------
class ChannelData(BaseModel):
    """Represents the JSON object stored in the 'data' column of the 'channels' table."""
    name: str
    description: Optional[str] = None
    global_note: Optional[str] = Field(None, alias="global")
    instruction: Optional[str] = None
    whitelist: List[str] = Field(default_factory=list)
    is_system_channel: bool = False


class Channel(BaseModel):
    """Represents a single row in the 'channels' table."""
    channel_id: str
    server_id: str
    server_name: str
    data: ChannelData  # The 'data' column is a validated JSON object


# ------------------------------------------------------
# Characters (maps to 'characters' and 'character_triggers' tables)
# ------------------------------------------------------
class CharacterData(BaseModel):
    """Represents the JSON object stored in the 'data' column of the 'characters' table."""
    persona: str
    examples: List[str]
    instructions: str
    avatar: Optional[str] = None
    info: Optional[str] = None


class Character(BaseModel):
    """
    Represents a fully assembled character, combining a row from the 'characters'
    table with its associated triggers from the 'character_triggers' table.
    """
    id: int
    name: str
    data: CharacterData  # The 'data' column is a validated JSON object
    triggers: List[str] = Field(default_factory=list)


# ------------------------------------------------------
# Presets (maps to the 'presets' table)
# ------------------------------------------------------
class Preset(BaseModel):
    """Represents a single row in the 'presets' table."""
    id: int
    name: str
    description: Optional[str] = None
    prompt_template: Optional[str] = None