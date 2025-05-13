# routers/config.py
"""Bot configuration API endpoints."""

import os
from fastapi import APIRouter, Body, HTTPException
from typing import List

from api.models.schemas import BotConfigModel, PatchOperation
from api.constants import CONFIG_FILE
from api.utils.file_operations import read_json_file, write_json_file, set_nested_value, remove_nested_value

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
    """Update the bot configuration."""
    config_dict = config.dict()
    write_json_file(CONFIG_FILE, config_dict)
    return config_dict

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