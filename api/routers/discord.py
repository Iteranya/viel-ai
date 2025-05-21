from fastapi import APIRouter,  HTTPException
import threading
import asyncio
from bot_run import client
from src.data.config_data import load_or_create_config
router = APIRouter()
_bot_thread = None
_bot_loop = None

def run_bot():
    global bot_loop, client
    config = load_or_create_config()
    discord_token = config.discord_key
    
    # Create new event loop for this thread
    bot_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(bot_loop)
    
    try:
        bot_loop.run_until_complete(client.start(discord_token))
    except Exception as e:
        print(f'Bot crashed: {e}')
    finally:
        # Ensure loop is properly closed
        if not bot_loop.is_closed():
            bot_loop.close()
        bot_loop = None

@router.post("/discord/activate")
async def activate_bot():
    global bot_thread, client
    
    # Check if bot is already running
    if client and not client.is_closed:
        raise HTTPException(status_code=400, detail="Bot is already active")
    
    # Create a new client instance if needed
    if client is None or client.is_closed:
        # Recreate your Discord client here
        # client = discord.Client(intents=your_intents)
        # or however you initialize your client
        pass
    
    # Start Discord client in background thread
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Wait a moment for the bot to initialize
    await asyncio.sleep(1)
    
    return {"success": True}

@router.post("/discord/deactivate")
async def deactivate_bot():
    global bot_loop, bot_thread, client
    
    if not client or client.is_closed:
        raise HTTPException(status_code=400, detail="Bot is not running")
   
    try:
        # Schedule client closure in the bot's event loop and wait for it
        if bot_loop and not bot_loop.is_closed():
            future = asyncio.run_coroutine_threadsafe(client.close(), bot_loop)
            # Wait for the close operation to complete (with timeout)
            future.result(timeout=10)
        
        # Wait for the thread to finish
        if bot_thread and bot_thread.is_alive():
            bot_thread.join(timeout=5)
        
        # Clean up references
        bot_thread = None
        client = None  # You'll need to recreate this for next activation
        
        return {"success": True}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deactivating bot: {str(e)}")

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