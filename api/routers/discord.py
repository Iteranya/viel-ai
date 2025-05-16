from fastapi import APIRouter, BackgroundTasks, HTTPException
import threading
import asyncio
from bot_run import client
from src.data.config_data import load_or_create_config
router = APIRouter()
_bot_thread = None

# Function to run the Discord client
def _run_bot():
    # Using a new event loop in this thread
    config = load_or_create_config()
    discord_token = config.discord_key
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.start(discord_token))

@router.post("/discord/activate")
async def activate_bot():
    global _bot_thread
    if client.is_ready():
        raise HTTPException(status_code=400, detail="Bot is already active")
    # Start Discord client in background thread
    _bot_thread = threading.Thread(target=_run_bot, daemon=True)
    _bot_thread.start()
    return {"success": True}

@router.post("/discord/deactivate")
async def deactivate_bot():
    if not client.is_ready():
        raise HTTPException(status_code=400, detail="Bot is not running")
    
    try:
        # Close the client in the same event loop it was created in
        await client.close()
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/discord/status")
async def check_bot_status():
    try:
        if client.is_ready():
            return {"status": "active"}
        else:
            return {"status": "inactive"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}