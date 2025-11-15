# routers/servers.py
"""Server and channel-related API endpoints, powered by the database."""

from fastapi import APIRouter, Body, Path, HTTPException, status
from typing import List

# --- Model and Database Imports ---
from api.models.models import Server, Channel, ChannelData
from api.db.database import Database
from pydantic import BaseModel

# --- Initialize Database Client ---
db = Database()

router = APIRouter(
    prefix="/api/servers",
    tags=["Servers & Channels"]
)

# --- Server Endpoints ---

@router.get("/", response_model=List[Server])
async def list_servers():
    """List all servers available in the database."""
    try:
        return db.list_servers()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Server, status_code=status.HTTP_201_CREATED)
async def create_server(server: Server = Body(..., description="Server data to create")):
    """Create a new server record in the database."""
    if db.get_server(server.server_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Server with ID '{server.server_id}' already exists."
        )
    try:
        db.create_server(
            server_id=server.server_id,
            server_name=server.server_name,
            description=server.description,
            instruction=server.instruction
        )
        return server
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create server: {e}")

@router.get("/{server_id}", response_model=Server)
async def get_server(server_id: str = Path(..., description="The unique ID of the server")):
    """Get a specific server's configuration."""
    server = db.get_server(server_id)
    if not server:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Server '{server_id}' not found")
    return server

@router.delete("/{server_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_server(server_id: str = Path(..., description="The unique ID of the server")):
    """
    Delete a server and all its associated channels from the database.
    This action is irreversible due to cascading deletes.
    """
    if not db.get_server(server_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Server '{server_id}' not found")
    try:
        db.delete_server(server_id)
        return None # Return empty response for 204
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete server: {e}")


# --- Channel Endpoints ---

# We need a request model because channel_id is provided by the client
class CreateChannelRequest(BaseModel):
    channel_id: str
    data: ChannelData

@router.post("/{server_id}/channels", response_model=Channel, status_code=status.HTTP_201_CREATED)
async def create_channel(
    server_id: str = Path(..., description="The server ID to add the channel to"),
    request: CreateChannelRequest = Body(..., description="The new channel's ID and configuration")
):
    """Create a new channel configuration within a specific server."""
    server = db.get_server(server_id)
    if not server:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Server '{server_id}' not found")
    if db.get_channel(request.channel_id):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Channel with ID '{request.channel_id}' already exists."
        )

    try:
        # Use by_alias=True to correctly handle the 'global' field name
        channel_data_dict = request.data.model_dump(by_alias=True)
        db.create_channel(
            channel_id=request.channel_id,
            server_id=server_id,
            server_name=server["server_name"],
            data=channel_data_dict
        )
        # Fetch the newly created channel to return the full object
        return db.get_channel(request.channel_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create channel: {e}")

@router.get("/{server_id}/channels", response_model=List[Channel])
async def list_channels_in_server(server_id: str = Path(..., description="The unique ID of the server")):
    """List all channels in a specific server."""
    if not db.get_server(server_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Server '{server_id}' not found")
    return db.list_channels_for_server(server_id)

@router.get("/{server_id}/channels/{channel_id}", response_model=Channel)
async def get_channel(
    server_id: str = Path(..., description="The server ID"),
    channel_id: str = Path(..., description="The unique channel ID")
):
    """Get a specific channel's configuration."""
    channel = db.get_channel(channel_id)
    if not channel or channel['server_id'] != server_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Channel '{channel_id}' not found in server '{server_id}'")
    return channel

@router.put("/{server_id}/channels/{channel_id}", response_model=Channel)
async def update_channel(
    server_id: str = Path(..., description="The server ID"),
    channel_id: str = Path(..., description="The unique channel ID"),
    channel_data: ChannelData = Body(..., description="The updated channel data")
):
    """Update an existing channel's configuration."""
    existing_channel = db.get_channel(channel_id)
    if not existing_channel or existing_channel['server_id'] != server_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Channel '{channel_id}' not found in server '{server_id}'")

    try:
        # Use by_alias=True to correctly handle the 'global' field name
        channel_data_dict = channel_data.model_dump(by_alias=True)
        db.update_channel(channel_id, data=channel_data_dict)
        return db.get_channel(channel_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update channel: {e}")

@router.delete("/{server_id}/channels/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(
    server_id: str = Path(..., description="The server ID"),
    channel_id: str = Path(..., description="The unique channel ID")
):
    """Delete a channel's configuration."""
    existing_channel = db.get_channel(channel_id)
    if not existing_channel or existing_channel['server_id'] != server_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Channel '{channel_id}' not found in server '{server_id}'")

    try:
        db.delete_channel(channel_id)
        return None
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete channel: {e}")