from fastapi import APIRouter,  HTTPException
import threading
import asyncio
from bot_run import client, start_bot
from src.data.config_data import load_or_create_config
router = APIRouter()
_bot_thread = None
_bot_loop = None

# Function to run the Discord client
def _run_bot():
    global _bot_loop
    config = load_or_create_config()
    # Using a new event loop in this thread
    _bot_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_bot_loop)
    try:
        _bot_loop.run_until_complete(start_bot(config))
    except Exception as e:
        print(f'Bot crashed: {e}')
    finally:
        _bot_loop.close()

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
        if _bot_loop and _bot_loop.is_running():
            asyncio.run_coroutine_threadsafe(client.close(), _bot_loop)
            return {"success": True}
        else:
            raise HTTPException(status_code=500, detail='Bot is not running')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/discord/status")
async def check_bot_status():
    try:
        if client.is_ready():
            return {"status": "active"}
        elif _bot_thread and _bot_thread.is_alive():
            return {"status": "starting"}
        else:
            return {"status": "inactive"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
    
@router.get("/discord/invite")
async def get_discord_invite():
    try:
        if client.is_ready():
            app_info = await client.application_info()
            invite_url = f"https://discord.com/oauth2/authorize?client_id={app_info.id}&scope=bot&permissions=8"
            return {"status": "active", "invite": invite_url}
        else:
            return {"status": "inactive"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


