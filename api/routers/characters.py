# routers/characters.py
"""Character-related API endpoints."""

import os
from fastapi import APIRouter, Body, Path, HTTPException
from fastapi.responses import JSONResponse
from pathlib import Path as FilePath
from typing import List

from api.models.schemas import CharacterModel, PatchOperation
from api.constants import CHARACTERS_DIR
from api.utils.file_operations import read_json_file, write_json_file, set_nested_value, remove_nested_value

router = APIRouter(
    prefix="/characters",
    tags=["Characters"]
)

@router.get("/", response_model=List[str])
async def list_characters():
    """List all available characters."""
    try:
        if not os.path.exists(CHARACTERS_DIR):
            return []
        return [f.stem for f in FilePath(CHARACTERS_DIR).glob("*.json")]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{character_name}", response_model=CharacterModel)
async def get_character(character_name: str = Path(..., description="Name of the character")):
    """Get a character's configuration."""
    file_path = f"{CHARACTERS_DIR}/{character_name}.json"
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"Character '{character_name}' not found")
    
    data = read_json_file(file_path)
    return data

@router.post("/{character_name}", response_model=CharacterModel)
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

@router.put("/{character_name}", response_model=CharacterModel)
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

@router.patch("/{character_name}", response_model=CharacterModel)
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

@router.delete("/{character_name}")
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