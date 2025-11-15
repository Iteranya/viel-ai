# routers/presets.py
"""Preset-related API endpoints, powered by the database."""

from fastapi import APIRouter, Body, Path, HTTPException, status
from typing import List
from pydantic import BaseModel

# --- Model and Database Imports ---
from api.models.models import Preset  # This model includes the 'id'
from api.db.database import Database

# --- Initialize Database Client ---
db = Database()

router = APIRouter(
    prefix="/api/presets",
    tags=["Presets"]
)

# --- Request Body Model ---
# This model is used for creating and updating presets, as the client
# does not provide the database-generated 'id'.
class PresetBody(BaseModel):
    name: str
    description: str | None = None
    prompt_template: str | None = None


@router.get("/", response_model=List[Preset])
async def list_presets():
    """List all available presets from the database."""
    try:
        return db.list_presets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@router.post("/", response_model=Preset, status_code=status.HTTP_201_CREATED)
async def create_preset(preset_data: PresetBody = Body(..., description="The new preset's data")):
    """Create a new preset in the database."""
    # Check for conflicts first
    if db.get_preset(name=preset_data.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Preset with name '{preset_data.name}' already exists."
        )
    try:
        # Create the preset in the database
        db.create_preset(
            name=preset_data.name,
            description=preset_data.description,
            prompt_template=preset_data.prompt_template
        )
        # Fetch the newly created preset to return the full object with its ID
        new_preset = db.get_preset(name=preset_data.name)
        if not new_preset:
            raise HTTPException(status_code=500, detail="Failed to retrieve preset after creation.")
        return new_preset
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create preset: {e}")


@router.get("/{preset_name}", response_model=Preset)
async def get_preset(preset_name: str = Path(..., description="The unique name of the preset")):
    """Get a specific preset's configuration by its name."""
    preset = db.get_preset(name=preset_name)
    if not preset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preset '{preset_name}' not found"
        )
    return preset


@router.put("/{preset_name}", response_model=Preset)
async def update_preset(
    preset_name: str = Path(..., description="The name of the preset to update"),
    preset_data: PresetBody = Body(..., description="The updated preset data")
):
    """Update an existing preset's data."""
    # Ensure the preset to be updated exists
    if not db.get_preset(name=preset_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preset '{preset_name}' not found"
        )
    # If the name is being changed, ensure the new name doesn't conflict with another preset
    if preset_name != preset_data.name and db.get_preset(name=preset_data.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Another preset with the name '{preset_data.name}' already exists."
        )

    try:
        db.update_preset(name=preset_name, **preset_data.model_dump())
        # Fetch and return the updated preset using its new name
        return db.get_preset(name=preset_data.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update preset: {e}")


@router.delete("/{preset_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_preset(preset_name: str = Path(..., description="The name of the preset to delete")):
    """Delete a preset from the database."""
    # Check if the preset exists before trying to delete
    if not db.get_preset(name=preset_name):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Preset '{preset_name}' not found"
        )

    try:
        db.delete_preset(name=preset_name)
        return None  # Return an empty response for 204 No Content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete preset: {e}")