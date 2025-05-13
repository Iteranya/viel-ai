from fastapi import FastAPI, HTTPException, Body, Path, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Union
import json
import os
from pathlib import Path as FilePath

app = FastAPI(title="Configuration Manager API", 
              description="API for managing character, channel, and bot configurations")

# Constants for file paths
CHARACTERS_DIR = "res/characters"
SERVERS_DIR = "res/servers"
CONFIG_FILE = "configurations/bot_config.json"

# Ensure directories exist
os.makedirs(CHARACTERS_DIR, exist_ok=True)
os.makedirs(SERVERS_DIR, exist_ok=True)
os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

app.mount("/interface", StaticFiles(directory="interface"), name="interface")

# Models for request/response validation
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
    default_character: str = Field("Vida-chan", description="Default character name")
    ai_endpoint: str = Field("https://generativelanguage.googleapis.com/v1beta/openai/", 
                           description="AI API endpoint")
    base_llm: str = Field("gemini-2.5-pro-exp-03-25", description="Base LLM model name")
    temperature: float = Field(0.5, description="Temperature setting for AI generation")
    ai_key: str = Field("", description="AI API key")
    discord_key: str = Field("", description="Discord API key")
    
    class Config:
        schema_extra = {
            "example": {
                "default_character": "Vida-chan",
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

# Helper functions
def read_json_file(file_path: str) -> dict:
    """Read and parse a JSON file."""
    try:
        if not os.path.exists(file_path):
            return {}
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in file: {file_path}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

def write_json_file(file_path: str, data: dict) -> None:
    """Write data to a JSON file."""
    try:
        # Ensure the directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error writing file: {str(e)}")

def get_nested_value(data: dict, path: str):
    """Get a value from a nested dictionary using a path like 'key1/key2'."""
    keys = path.strip('/').split('/')
    current = data
    for key in keys:
        if key not in current:
            return None
        current = current[key]
    return current

def set_nested_value(data: dict, path: str, value: Any) -> dict:
    """Set a value in a nested dictionary using a path like 'key1/key2'."""
    keys = path.strip('/').split('/')
    if not keys:
        return data
    
    current = data
    for i, key in enumerate(keys[:-1]):
        if key not in current:
            current[key] = {}
        elif not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    
    current[keys[-1]] = value
    return data

def remove_nested_value(data: dict, path: str) -> dict:
    """Remove a value from a nested dictionary using a path like 'key1/key2'."""
    keys = path.strip('/').split('/')
    if not keys:
        return data
    
    current = data
    for i, key in enumerate(keys[:-1]):
        if key not in current:
            return data
        current = current[key]
    
    if keys[-1] in current:
        del current[keys[-1]]
    
    return data

@app.get("/", response_class=HTMLResponse)
async def get_html():
    template_path = "index.html"
    with open(template_path, "r") as f:
        html = f.read()

    return html

@app.get("/new", response_class=HTMLResponse)
async def get_html():
    template_path = "interface/index.html"
    with open(template_path, "r") as f:
        html = f.read()

    return html

# Character Endpoints
@app.get("/characters", response_model=List[str], tags=["Characters"])
async def list_characters():
    """List all available characters."""
    try:
        if not os.path.exists(CHARACTERS_DIR):
            return []
        return [f.stem for f in FilePath(CHARACTERS_DIR).glob("*.json")]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/characters/{character_name}", response_model=CharacterModel, tags=["Characters"])
async def get_character(character_name: str = Path(..., description="Name of the character")):
    """Get a character's configuration."""
    file_path = f"{CHARACTERS_DIR}/{character_name}.json"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Character '{character_name}' not found")
    
    data = read_json_file(file_path)
    return data

@app.post("/characters/{character_name}", response_model=CharacterModel, tags=["Characters"])
async def create_character(
    character_name: str = Path(..., description="Name of the character"),
    character: CharacterModel = Body(..., description="Character data")
):
    """Create a new character configuration."""
    file_path = f"{CHARACTERS_DIR}/{character_name}.json"
    if os.path.exists(file_path):
        raise HTTPException(status_code=409, detail=f"Character '{character_name}' already exists")
    
    character_dict = character.dict()
    write_json_file(file_path, character_dict)
    return character_dict

@app.put("/characters/{character_name}", response_model=CharacterModel, tags=["Characters"])
async def update_character(
    character_name: str = Path(..., description="Name of the character"),
    character: CharacterModel = Body(..., description="Updated character data")
):
    """Update an existing character configuration."""
    file_path = f"{CHARACTERS_DIR}/{character_name}.json"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Character '{character_name}' not found")
    
    character_dict = character.dict()
    write_json_file(file_path, character_dict)
    return character_dict

@app.patch("/characters/{character_name}", response_model=CharacterModel, tags=["Characters"])
async def patch_character(
    character_name: str = Path(..., description="Name of the character"),
    operations: List[PatchOperation] = Body(..., description="Patch operations")
):
    """Partially update a character configuration."""
    file_path = f"{CHARACTERS_DIR}/{character_name}.json"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Character '{character_name}' not found")
    
    data = read_json_file(file_path)
    
    for op in operations:
        if op.op == "replace":
            data = set_nested_value(data, op.path, op.value)
        elif op.op == "add":
            data = set_nested_value(data, op.path, op.value)
        elif op.op == "remove":
            data = remove_nested_value(data, op.path)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported operation: {op.op}")
    
    write_json_file(file_path, data)
    return data

@app.delete("/characters/{character_name}", tags=["Characters"])
async def delete_character(character_name: str = Path(..., description="Name of the character")):
    """Delete a character configuration."""
    file_path = f"{CHARACTERS_DIR}/{character_name}.json"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Character '{character_name}' not found")
    
    try:
        os.remove(file_path)
        return JSONResponse(content={"message": f"Character '{character_name}' deleted successfully"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete character: {str(e)}")

# Channel Endpoints
@app.get("/servers", response_model=List[str], tags=["Servers"])
async def list_servers():
    """List all available servers."""
    try:
        if not os.path.exists(SERVERS_DIR):
            return []
        return [d.name for d in FilePath(SERVERS_DIR).iterdir() if d.is_dir()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/servers/{server_name}/channels", response_model=List[str], tags=["Channels"])
async def list_channels(server_name: str = Path(..., description="Name of the server")):
    """List all channels in a server."""
    server_dir = f"{SERVERS_DIR}/{server_name}"
    if not os.path.exists(server_dir):
        raise HTTPException(status_code=404, detail=f"Server '{server_name}' not found")
    
    try:
        return [f.stem for f in FilePath(server_dir).glob("*.json")]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/servers/{server_name}/channels/{channel_name}", response_model=ChannelModel, tags=["Channels"])
async def get_channel(
    server_name: str = Path(..., description="Name of the server"),
    channel_name: str = Path(..., description="Name of the channel")
):
    """Get a channel's configuration."""
    file_path = f"{SERVERS_DIR}/{server_name}/{channel_name}.json"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Channel '{channel_name}' not found in server '{server_name}'")
    
    data = read_json_file(file_path)
    return data

@app.post("/servers/{server_name}/channels/{channel_name}", response_model=ChannelModel, tags=["Channels"])
async def create_channel(
    server_name: str = Path(..., description="Name of the server"),
    channel_name: str = Path(..., description="Name of the channel"),
    channel: ChannelModel = Body(..., description="Channel data")
):
    """Create a new channel configuration."""
    server_dir = f"{SERVERS_DIR}/{server_name}"
    os.makedirs(server_dir, exist_ok=True)
    
    file_path = f"{server_dir}/{channel_name}.json"
    if os.path.exists(file_path):
        raise HTTPException(
            status_code=409, 
            detail=f"Channel '{channel_name}' already exists in server '{server_name}'"
        )
    
    channel_dict = channel.dict()
    write_json_file(file_path, channel_dict)
    return channel_dict

@app.put("/servers/{server_name}/channels/{channel_name}", response_model=ChannelModel, tags=["Channels"])
async def update_channel(
    server_name: str = Path(..., description="Name of the server"),
    channel_name: str = Path(..., description="Name of the channel"),
    channel: ChannelModel = Body(..., description="Updated channel data")
):
    """Update an existing channel configuration."""
    file_path = f"{SERVERS_DIR}/{server_name}/{channel_name}.json"
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404, 
            detail=f"Channel '{channel_name}' not found in server '{server_name}'"
        )
    
    channel_dict = channel.dict()
    write_json_file(file_path, channel_dict)
    return channel_dict

@app.patch("/servers/{server_name}/channels/{channel_name}", response_model=ChannelModel, tags=["Channels"])
async def patch_channel(
    server_name: str = Path(..., description="Name of the server"),
    channel_name: str = Path(..., description="Name of the channel"),
    operations: List[PatchOperation] = Body(..., description="Patch operations")
):
    """Partially update a channel configuration."""
    file_path = f"{SERVERS_DIR}/{server_name}/{channel_name}.json"
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404, 
            detail=f"Channel '{channel_name}' not found in server '{server_name}'"
        )
    
    data = read_json_file(file_path)
    
    for op in operations:
        if op.op == "replace":
            data = set_nested_value(data, op.path, op.value)
        elif op.op == "add":
            data = set_nested_value(data, op.path, op.value)
        elif op.op == "remove":
            data = remove_nested_value(data, op.path)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported operation: {op.op}")
    
    write_json_file(file_path, data)
    return data

@app.delete("/servers/{server_name}/channels/{channel_name}", tags=["Channels"])
async def delete_channel(
    server_name: str = Path(..., description="Name of the server"),
    channel_name: str = Path(..., description="Name of the channel")
):
    """Delete a channel configuration."""
    file_path = f"{SERVERS_DIR}/{server_name}/{channel_name}.json"
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404, 
            detail=f"Channel '{channel_name}' not found in server '{server_name}'"
        )
    
    try:
        os.remove(file_path)
        return JSONResponse(
            content={"message": f"Channel '{channel_name}' in server '{server_name}' deleted successfully"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete channel: {str(e)}")

# Bot Config Endpoints
@app.get("/config", response_model=BotConfigModel, tags=["Bot Configuration"])
async def get_config():
    """Get the bot configuration."""
    if not os.path.exists(CONFIG_FILE):
        # Return default config if file doesn't exist yet
        return BotConfigModel()
    
    data = read_json_file(CONFIG_FILE)
    return data

@app.put("/config", response_model=BotConfigModel, tags=["Bot Configuration"])
async def update_config(config: BotConfigModel = Body(..., description="Updated bot configuration")):
    """Update the bot configuration."""
    config_dict = config.dict()
    write_json_file(CONFIG_FILE, config_dict)
    return config_dict

@app.patch("/config", response_model=BotConfigModel, tags=["Bot Configuration"])
async def patch_config(operations: List[PatchOperation] = Body(..., description="Patch operations")):
    """Partially update the bot configuration."""
    if not os.path.exists(CONFIG_FILE):
        data = BotConfigModel().dict()
    else:
        data = read_json_file(CONFIG_FILE)
    
    for op in operations:
        if op.op == "replace":
            data = set_nested_value(data, op.path, op.value)
        elif op.op == "add":
            data = set_nested_value(data, op.path, op.value)
        elif op.op == "remove":
            data = remove_nested_value(data, op.path)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported operation: {op.op}")
    
    write_json_file(CONFIG_FILE, data)
    return data
from fastapi.middleware.cors import CORSMiddleware

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5666)