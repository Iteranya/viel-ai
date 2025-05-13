# routers/config.py
"""Bot configuration API endpoints."""

import os
from fastapi import APIRouter, Body, HTTPException
from typing import List, Set
import json
from api.models.schemas import BotConfigModel, PatchOperation
from api.constants import CONFIG_FILE
from api.utils.file_operations import read_json_file, write_json_file, set_nested_value, remove_nested_value
PRESERVE_FIELDS: Set[str] = {'ai_key', 'discord_key'}

REQUIRED_FIELDS: Set[str] = {'default_character', 'ai_endpoint', 'base_llm'}

router = APIRouter(
    prefix="/config",
    tags=["Bot Configuration"]
)

@router.get("/", response_model=BotConfigModel)
async def get_config():
    """Get the bot configuration."""
    if not os.path.exists(CONFIG_FILE):
        # Return default config if file doesn't exist yet
        return BotConfigModel()
    
    data = read_json_file(CONFIG_FILE)
    return data

@router.put("/", response_model=BotConfigModel)
async def update_config(config: BotConfigModel = Body(..., description="Updated bot configuration")):
    """Update the bot configuration with smart field preservation."""
    try:
        # Load existing config if file exists
        existing_config = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
        
        # Convert new config to dict
        new_config = config.dict()
        
        # Validate required fields aren't being set to empty
        for field in REQUIRED_FIELDS:
            if new_config.get(field, '').strip() == '':
                raise HTTPException(
                    status_code=400,
                    detail=f"Field '{field}' cannot be empty"
                )
        
        # Preserve existing values for specified fields if new value is empty
        for field in PRESERVE_FIELDS:
            if (field in existing_config and 
                field in new_config and 
                str(new_config[field]).strip() == ''):
                new_config[field] = existing_config[field]
        
        # Write the merged config
        write_json_file(CONFIG_FILE, new_config)
        return new_config
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating config: {str(e)}")

@router.patch("/", response_model=BotConfigModel)
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