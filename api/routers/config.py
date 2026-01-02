# routers/config.py
"""Bot configuration API endpoints, powered by the database."""

from fastapi import APIRouter, Body, HTTPException
from typing import Set
# Assumes your db class is at api/db/database.py
from api.db.database import Database
from api.models.models import BotConfig

# --- Constants and DB Initialization ---
# This business logic is preserved from your original file.
PRESERVE_FIELDS: Set[str] = {'ai_key', 'discord_key','multimodal_ai_api'}
REQUIRED_FIELDS: Set[str] = {'default_character', 'ai_endpoint', 'base_llm'}

db = Database()

router = APIRouter(
    prefix="/api/config",
    tags=["Bot Configuration"]
)

@router.get("/", response_model=BotConfig)
async def get_config():
    """Get the bot configuration from the database."""
    try:
        # Fetch all key-value pairs from the config table
        all_db_configs = db.list_configs()
        # Pydantic will use default values for any keys not found in the DB
        return BotConfig(**all_db_configs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error while fetching config: {e}")


@router.put("/", response_model=BotConfig)
async def update_config(config: BotConfig = Body(..., description="Updated bot configuration")):
    """
    Update the bot configuration in the database with smart field preservation.
    Each field in the model is saved as a separate key-value pair.
    """
    try:
        # Load existing config from the database
        existing_config = db.list_configs()

        # Convert new incoming config to a dictionary
        new_config = config.model_dump()

        # Validate that required fields are not empty or just whitespace
        for field in REQUIRED_FIELDS:
            if not str(new_config.get(field, '')).strip():
                raise HTTPException(
                    status_code=400,
                    detail=f"Required field '{field}' cannot be empty"
                )

        # Preserve existing sensitive values (like keys) if the new value is empty
        for field in PRESERVE_FIELDS:
            if (field in existing_config and
                not str(new_config.get(field, '')).strip()):
                new_config[field] = existing_config[field]

        # Write each key-value pair from the final, merged config to the database
        for key, value in new_config.items():
            # Ensure value is not None before storing, as some fields are Optional
            if value is not None:
                db.set_config(key, value)

        return new_config
    except HTTPException:
        # Re-raise validation errors directly
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating config in database: {e}")