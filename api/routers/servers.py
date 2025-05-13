# routers/servers.py
"""Server and channel-related API endpoints."""

import os
from fastapi import APIRouter, Body, Path, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path as FilePath
from typing import List

from api.models.schemas import ChannelModel, PatchOperation
from api.constants import SERVERS_DIR
from api.utils.file_operations import read_json_file, write_json_file, set_nested_value, remove_nested_value

router = APIRouter(
    prefix="/servers",
    tags=["Servers"]
)

@router.get("/", response_model=List[str])
async def list_servers():
    """List all available servers."""
    try:
        if not os.path.exists(SERVERS_DIR):
            return []
        return [d.name for d in FilePath(SERVERS_DIR).iterdir() if d.is_dir()]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{server_name}/channels", response_model=List[str], tags=["Channels"])
async def list_channels(server_name: str = Path(..., description="Name of the server")):
    """List all channels in a server."""
    server_dir = f"{SERVERS_DIR}/{server_name}"
    if not os.path.exists(server_dir):
        raise HTTPException(status_code=404, detail=f"Server '{server_name}' not found")
    
    try:
        return [f.stem for f in FilePath(server_dir).glob("*.json")]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{server_name}/channels/{channel_name}", response_model=ChannelModel, tags=["Channels"])
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

@router.post("/{server_name}/channels/{channel_name}", response_model=ChannelModel, tags=["Channels"])
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

@router.put("/{server_name}/channels/{channel_name}", response_model=ChannelModel, tags=["Channels"])
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

@router.patch("/{server_name}/channels/{channel_name}", response_model=ChannelModel, tags=["Channels"])
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

@router.delete("/{server_name}/channels/{channel_name}", tags=["Channels"])
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