from fastapi import APIRouter, HTTPException
import threading
import asyncio
import time
from bot_run import client
from src.data.config_data import load_or_create_config

router = APIRouter()
_bot_thread = None
_bot_loop = None
_shutdown_event = None

# Function to run the Discord client
def _run_bot():
    global _bot_loop, _shutdown_event
    config = load_or_create_config()
    discord_token = config.discord_key
    
    # Create new event loop for this thread
    _bot_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(_bot_loop)
    _shutdown_event = asyncio.Event()
    
    async def bot_runner():
        try:
            # Start the bot
            await client.start(discord_token)
        except asyncio.CancelledError:
            print("Bot startup was cancelled")
        except Exception as e:
            print(f'Bot crashed: {e}')
        finally:
            # Ensure client is closed
            if not client.is_closed():
                await client.close()
            
            # Cancel all remaining tasks
            tasks = [t for t in asyncio.all_tasks(_bot_loop) if not t.done()]
            if tasks:
                print(f"Cancelling {len(tasks)} pending tasks...")
                for task in tasks:
                    task.cancel()
                
                # Wait for tasks to complete cancellation
                await asyncio.gather(*tasks, return_exceptions=True)
            
            _shutdown_event.set()
    
    try:
        _bot_loop.run_until_complete(bot_runner())
    finally:
        # Clean shutdown of the loop
        try:
            # Cancel any remaining tasks
            pending = asyncio.all_tasks(_bot_loop)
            for task in pending:
                task.cancel()
            
            if pending:
                _bot_loop.run_until_complete(
                    asyncio.gather(*pending, return_exceptions=True)
                )
        except Exception as e:
            print(f"Error during cleanup: {e}")
        finally:
            _bot_loop.close()
            print("Bot thread shutting down...")

@router.post("/discord/activate")
async def activate_bot():
    global _bot_thread
    
    # Check if bot is already running
    if _bot_thread and _bot_thread.is_alive():
        if client.is_ready():
            raise HTTPException(status_code=400, detail="Bot is already active")
        else:
            raise HTTPException(status_code=400, detail="Bot is starting up")
    
    # Start Discord client in background thread
    _bot_thread = threading.Thread(target=_run_bot, daemon=True)
    _bot_thread.start()
    
    # Wait a moment to check if startup was successful
    await asyncio.sleep(1)
    
    return {"success": True, "message": "Bot activation initiated"}

@router.post("/discord/deactivate")
async def deactivate_bot():
    global _bot_thread, _bot_loop, _shutdown_event
    
    if not _bot_thread or not _bot_thread.is_alive():
        raise HTTPException(status_code=400, detail="Bot is not running")
    
    if not client.is_ready() and not (_bot_loop and _bot_loop.is_running()):
        raise HTTPException(status_code=400, detail="Bot is not active")
    
    try:
        # Schedule bot shutdown in its own event loop
        if _bot_loop and _bot_loop.is_running():
            # Create a future to track the shutdown
            future = asyncio.run_coroutine_threadsafe(client.close(), _bot_loop)
            
            # Wait for shutdown to complete (with timeout)
            try:
                future.result(timeout=10)  # 10 second timeout
            except Exception as e:
                print(f"Error during bot shutdown: {e}")
        
        # Wait for the bot thread to finish (with timeout)
        if _bot_thread.is_alive():
            _bot_thread.join(timeout=15)  # 15 second timeout
            
            if _bot_thread.is_alive():
                print("Warning: Bot thread did not shut down cleanly")
                raise HTTPException(status_code=500, detail="Bot shutdown timed out")
        
        # Reset global variables
        _bot_thread = None
        _bot_loop = None
        _shutdown_event = None
        
        return {"success": True, "message": "Bot deactivated successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during shutdown: {str(e)}")

@router.get("/discord/status")
async def check_bot_status():
    try:
        if client.is_ready():
            return {"status": "active", "bot_ready": True}
        elif _bot_thread and _bot_thread.is_alive():
            return {"status": "starting", "bot_ready": False}
        else:
            return {"status": "inactive", "bot_ready": False}
    except Exception as e:
        return {"status": "error", "detail": str(e), "bot_ready": False}