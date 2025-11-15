# routers/characters.py
"""Character-related API endpoints, powered by the database."""

from fastapi import APIRouter, Body, Path, HTTPException, Request
from typing import List

# --- Model and Database Imports ---
# Assumes your models and db class are structured like this
from api.models.models import Character, CharacterData 
from api.db.database import Database

# --- Initialize Database Client ---
# This creates a single instance of the Database class for the router to use.
db = Database()


router = APIRouter(
    prefix="/api/characters",
    tags=["Characters"]
)


def parse_character_card(raw_data: dict) -> tuple[str, dict]:
    """
    Parses different character card formats (Pygmalion, Viel) and returns
    a tuple of (name, data_dict) ready for the database.
    The data_dict corresponds to the CharacterData model.
    """
    # Try parsing as a Pygmalion/SillyTavern card
    if raw_data.get("data"):
        raw_data = raw_data.get("data")

    if "mes_example" in raw_data:
        try:
            name = raw_data.get("name")
            if not name:
                raise ValueError("Character name is missing from the card.")

            description = raw_data.get("description", "")
            examples_str = raw_data.get("mes_example", "")
            personality = raw_data.get("personality", "")
            system_prompt = raw_data.get("system_prompt", "")
            post_history = raw_data.get("post_history_instructions", "")
            avatar = raw_data.get("avatar", None)

            # Replace placeholders
            description = description.replace("{{user}}", "User").replace("{{char}}", name)
            examples_str = examples_str.replace("{{user}}", "User").replace("{{char}}", name)

            # Assemble the data into the CharacterData structure
            character_data = {
                "persona": f"<description>{description}</description>\n<personality>{personality}</personality>",
                "examples": [examples_str] if examples_str else [],
                "instructions": f"[System Note: {system_prompt}]\n[System Note: {post_history}]",
                "avatar": avatar,
                "info": "Imported from Pygmalion/Tavern Card"
            }
            return name, character_data
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse Pygmalion/Tavern card: {e}")

    # Try parsing as a "Viel" type card (matching our internal structure)
    elif "persona" in raw_data:
        try:
            name = raw_data.get("name")
            if not name:
                raise ValueError("Character name is missing from the card.")

            character_data = {
                "persona": raw_data.get("persona", ""),
                "examples": raw_data.get("examples", []),
                "instructions": raw_data.get("instructions", ""),
                "avatar": raw_data.get("avatar", None),
                "info": raw_data.get("info", "Imported from Viel Card")
            }
            return name, character_data
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to parse Viel card: {e}")
    
    raise HTTPException(status_code=400, detail="Incompatible or unrecognized character card format.")


@router.get("/", response_model=List[str])
async def list_characters():
    """List all available character names from the database."""
    try:
        characters = db.list_characters()
        return [char["name"] for char in characters]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@router.get("/{character_name}", response_model=Character)
async def get_character(character_name: str = Path(..., description="Name of the character")):
    """Get a character's full configuration from the database."""
    character = db.get_character(name=character_name)
    if not character:
        raise HTTPException(status_code=404, detail=f"Character '{character_name}' not found")
    return character


@router.post("/import", response_model=Character)
async def create_character_from_import(request: Request):
    """
    Create a new character by importing from a raw JSON character card.
    This is the primary endpoint for creating new characters.
    """
    try:
        raw_data = await request.json()
        name, data_dict = parse_character_card(raw_data)
        
        # Check for conflicts
        if db.get_character(name=name):
            raise HTTPException(status_code=409, detail=f"Character '{name}' already exists.")
            
        # Create character in the database
        db.create_character(name=name, data=data_dict)
        
        # Fetch the newly created character to return the full object
        new_character = db.get_character(name=name)
        if not new_character:
            # This should not happen if creation was successful, but it's good practice
            raise HTTPException(status_code=500, detail="Failed to retrieve character after creation.")
            
        return new_character
    except HTTPException as e:
        # Re-raise known HTTP exceptions
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during import: {e}")


@router.put("/{character_name}", response_model=Character)
async def update_character(
    character_name: str = Path(..., description="Name of the character"),
    character_data: CharacterData = Body(..., description="The fields of the character to update")
):
    """Update an existing character's data in the database."""
    # Check if character exists
    if not db.get_character(name=character_name):
        raise HTTPException(status_code=404, detail=f"Character '{character_name}' not found")

    try:
        # The data argument in update_character expects a dict
        db.update_character(name=character_name, data=character_data.model_dump())
        
        # Fetch and return the updated character
        updated_character = db.get_character(name=character_name)
        return updated_character
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update character: {e}")


@router.delete("/{character_name}")
async def delete_character(character_name: str = Path(..., description="Name of the character")):
    """Delete a character from the database."""
    # Check if character exists before trying to delete
    if not db.get_character(name=character_name):
        raise HTTPException(status_code=404, detail=f"Character '{character_name}' not found")
    
    try:
        db.delete_character(name=character_name)
        return {"message": f"Character '{character_name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete character: {e}")