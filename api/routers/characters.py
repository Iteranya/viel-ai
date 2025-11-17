# routers/characters.py
"""
Character-related API endpoints, powered by the database.

This file manages the full lifecycle of characters via RESTful endpoints:
- GET /: Lists all characters in a lightweight format for grids/UIs.
- POST /: Creates a new character from a structured JSON object (the primary creation method).
- GET /{name}: Retrieves the full details of a single character.
- PUT /{name}: Updates an existing character's data and triggers.
- DELETE /{name}: Removes a character.
- POST /import: A secondary creation method for importing from raw character card files.
- POST /upload_image: A utility endpoint to upload avatars via the Discord bot.
"""

import asyncio
from fastapi import APIRouter, Body, Path, HTTPException, Request, UploadFile, File, status
from typing import List, Annotated

# --- Model and Database Imports ---
# These Pydantic models define the structure of data for requests and responses.
from api.models.models import (
    Character,          # The full character object (DB row + data + triggers)
    CharacterData,      # The core character definition (persona, examples, etc.)
    CharacterCreate,    # The required structure for POST / requests
    CharacterUpdate,    # The required structure for PUT /{name} requests
    CharacterListItem   # The lightweight structure for GET / responses
)
from api.db.database import Database

# This is the global bot instance managed by your discord router
from api.bot_state import bot_state
from src.utils.image_uploader import upload_image_to_system_channel

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
    Used by the /import endpoint.
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


# --- Primary CRUD Endpoints ---

@router.get("/", response_model=List[CharacterListItem])
async def list_characters():
    """
    List all available characters with their name, avatar, and info.
    Uses the lightweight CharacterListItem model for efficiency.
    """
    try:
        characters = db.list_characters()
        result = []
        for char in characters:
            char_data = char.get("data", {})
            result.append(
                CharacterListItem(
                    name=char.get("name", ""),
                    avatar=char_data.get("avatar") or "",
                    info=char_data.get("info") or ""
                )
            )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


@router.post("/", response_model=Character, status_code=status.HTTP_201_CREATED)
async def create_character(
    character: CharacterCreate = Body(..., description="The character to create, including name, data, and triggers.")
):
    """
    Create a new character from a structured JSON object.
    This is the primary endpoint for creating characters from the UI form.
    """
    if db.get_character(name=character.name):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Character '{character.name}' already exists."
        )
    try:
        db.create_character(
            name=character.name,
            data=character.data.model_dump(),
            triggers=character.triggers
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An unexpected error occurred during character creation: {e}"
        )

    # Fetch and return the newly created character to confirm success
    new_character = db.get_character(name=character.name)
    if not new_character:
        raise HTTPException(status_code=500, detail="Failed to retrieve character after creation.")
    return new_character


@router.get("/{character_name}", response_model=Character)
async def get_character(character_name: str = Path(..., description="Name of the character")):
    """Get a character's full configuration from the database."""
    character = db.get_character(name=character_name)
    if not character:
        raise HTTPException(status_code=404, detail=f"Character '{character_name}' not found")
    return character


@router.put("/{character_name}", response_model=Character)
async def update_character(
    character_name: str = Path(..., description="Name of the character to update"),
    character_update: CharacterUpdate = Body(..., description="The full character data and triggers to update")
):
    """Update an existing character's data and triggers in the database."""
    existing_char = db.get_character(name=character_name)
    if not existing_char:
        raise HTTPException(status_code=404, detail=f"Character '{character_name}' not found")

    try:
        # Step 1: Update the main character data (persona, examples, etc.)
        db.update_character(name=character_name, data=character_update.data.model_dump())
        
        # Step 2: Update the triggers by replacing them completely
        # This requires the character's database ID.
        db.update_character_triggers(character_id=existing_char['id'], triggers=character_update.triggers)
        
        # Step 3: Fetch and return the fully updated character object
        updated_character = db.get_character(name=character_name)
        return updated_character
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update character: {e}")


@router.delete("/{character_name}")
async def delete_character(character_name: str = Path(..., description="Name of the character")):
    """Delete a character from the database."""
    if not db.get_character(name=character_name):
        raise HTTPException(status_code=404, detail=f"Character '{character_name}' not found")
    
    try:
        db.delete_character(name=character_name)
        return {"message": f"Character '{character_name}' deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete character: {e}")
    

# --- Utility and Import Endpoints ---

@router.post("/import", response_model=Character, status_code=status.HTTP_201_CREATED)
async def create_character_from_import(request: Request):
    """
    Create a new character by importing from a raw JSON character card file.
    This is a secondary creation method, used by the 'Import Card' button.
    """
    try:
        raw_data = await request.json()
        name, data_dict = parse_character_card(raw_data)
        
        if db.get_character(name=name):
            raise HTTPException(status_code=409, detail=f"Character '{name}' already exists.")
            
        # Card imports don't have triggers, so an empty list is passed
        db.create_character(name=name, data=data_dict, triggers=[])
        
        new_character = db.get_character(name=name)
        if not new_character:
            raise HTTPException(status_code=500, detail="Failed to retrieve character after creation.")
            
        return new_character
    except HTTPException as e:
        raise e # Re-raise known HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during import: {e}")


@router.post("/upload_image", response_model=dict)
async def upload_image(
    image: Annotated[UploadFile, File(description="The image file to upload.")]
):
    """
    Accepts an image file, uploads it via the Discord bot, and returns the permanent Discord CDN link.
    """
    if not bot_state.bot_instance or not bot_state.bot_instance.is_ready():
        raise HTTPException(status_code=503, detail="The Discord bot is not active.")

    image_bytes = await image.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="No image data received.")

    # Run the synchronous Discord function in a separate thread to avoid blocking FastAPI
    cdn_url = await asyncio.to_thread(
        upload_image_to_system_channel,
        image_bytes=image_bytes,
        filename=image.filename,
        bot=bot_state.bot_instance
    )

    if not cdn_url:
        raise HTTPException(
            status_code=500,
            detail="Failed to upload image. Check server logs for Discord API errors or misconfigurations."
        )

    return {"filename": image.filename, "cdn_url": cdn_url}