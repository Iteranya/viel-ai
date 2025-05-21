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
    
    async def cleanup_tasks():
        """Safely cleanup all pending tasks"""
        try:
            # Get all tasks except current one
            current_task = asyncio.current_task(_bot_loop)
            all_tasks = [t for t in asyncio.all_tasks(_bot_loop) if t != current_task and not t.done()]
            
            if all_tasks:
                print(f"Cleaning up {len(all_tasks)} pending tasks...")
                
                # Cancel tasks in batches to avoid recursion issues
                batch_size = 10
                for i in range(0, len(all_tasks), batch_size):
                    batch = all_tasks[i:i + batch_size]
                    for task in batch:
                        if not task.done():
                            task.cancel()
                    
                    # Wait for this batch with timeout
                    try:
                        await asyncio.wait_for(
                            asyncio.gather(*batch, return_exceptions=True), 
                            timeout=2.0
                        )
                    except asyncio.TimeoutError:
                        print(f"Timeout waiting for batch {i//batch_size + 1}")
                        continue
                    except Exception as e:
                        print(f"Error in batch cleanup: {e}")
                        continue
                
                print("Task cleanup completed")
        except Exception as e:
            print(f"Error during task cleanup: {e}")
    
    async def bot_runner():
        try:
            # Start the bot
            await client.start(discord_token)
        except asyncio.CancelledError:
            print("Bot startup was cancelled")
        except Exception as e:
            print(f'Bot crashed: {e}')
        finally:
            print("Bot runner finalizing...")
            
            # Ensure client is closed first
            if not client.is_closed():
                try:
                    await asyncio.wait_for(client.close(), timeout=5.0)
                except asyncio.TimeoutError:
                    print("Timeout closing client")
                except Exception as e:
                    print(f"Error closing client: {e}")
            
            # Clean up remaining tasks
            await cleanup_tasks()
            _shutdown_event.set()
    
    try:
        _bot_loop.run_until_complete(bot_runner())
    except KeyboardInterrupt:
        print("Bot interrupted")
    finally:
        # Final cleanup with protection against hanging
        print("Final cleanup...")
        try:
            # Force close any remaining tasks with timeout
            remaining_tasks = [t for t in asyncio.all_tasks(_bot_loop) if not t.done()]
            if remaining_tasks:
                print(f"Force cancelling {len(remaining_tasks)} remaining tasks")
                for task in remaining_tasks:
                    task.cancel()
                
                # Give tasks a short time to cancel, then move on
                try:
                    _bot_loop.run_until_complete(
                        asyncio.wait_for(
                            asyncio.gather(*remaining_tasks, return_exceptions=True),
                            timeout=3.0
                        )
                    )
                except asyncio.TimeoutError:
                    print("Final cleanup timed out, proceeding with loop closure")
                except Exception as e:
                    print(f"Error in final cleanup: {e}")
        except Exception as e:
            print(f"Error during final cleanup: {e}")
        finally:
            try:
                _bot_loop.close()
            except Exception as e:
                print(f"Error closing loop: {e}")
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
        print("Initiating bot shutdown...")
        
        # First, try to gracefully close the client
        if _bot_loop and _bot_loop.is_running():
            try:
                # Schedule the close operation with timeout
                close_future = asyncio.run_coroutine_threadsafe(client.close(), _bot_loop)
                close_future.result(timeout=8)  # 8 second timeout for close
                print("Client closed successfully")
            except Exception as e:
                print(f"Error or timeout closing client: {e}")
        
        # Wait for shutdown event or timeout
        start_time = time.time()
        while _bot_thread.is_alive() and (time.time() - start_time) < 12:
            await asyncio.sleep(0.1)
        
        # If thread is still alive, give it a bit more time
        if _bot_thread.is_alive():
            print("Waiting for bot thread to finish...")
            _bot_thread.join(timeout=5)
            
            if _bot_thread.is_alive():
                print("Warning: Bot thread did not shut down cleanly within timeout")
                # Don't raise an exception, just log the warning
        
        # Reset global variables regardless of thread state
        _bot_thread = None
        _bot_loop = None
        _shutdown_event = None
        
        print("Bot shutdown completed")
        return {"success": True, "message": "Bot deactivated successfully"}
        
    except Exception as e:
        print(f"Exception during shutdown: {e}")
        # Still reset variables to allow restart
        _bot_thread = None
        _bot_loop = None
        _shutdown_event = None
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