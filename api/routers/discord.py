# api_router.py

import threading
import asyncio
import logging
import time
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse

# Adjust import paths to match your project structure
from bot_run import Viel
import discord

router = APIRouter(
    prefix="/api/discord",
    tags=["Discord Bot"]
)

# --- State Management ---
# These variables will hold the running bot instance and its thread
_bot_instance: Optional[Viel] = None
_bot_thread: Optional[threading.Thread] = None

# --- Logging Configuration ---
LOG_FILE_PATH = "discord_bot.log"

def setup_file_logging():
    """Configures the root logger to write to a file."""
    # Create a handler that writes log records to a file
    file_handler = logging.FileHandler(LOG_FILE_PATH, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # Create a formatter and set it for the handler
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    
    # Get the root logger and add the handler
    # This will capture logs from discord.py and our own print statements
    logging.basicConfig(handlers=[file_handler], level=logging.INFO, force=True)

def _run_bot_in_thread():
    """Target function for the bot's background thread."""
    global _bot_instance
    
    # Set up logging for this thread
    setup_file_logging()
    
    try:
        logging.info("--- Bot thread started. Initializing bot... ---")
        intents = discord.Intents.all()
        _bot_instance = Viel(intents=intents)
        # The run() method is blocking and contains the main loop
        _bot_instance.run()
        logging.info("--- Bot has shut down cleanly. ---")
    except Exception as e:
        logging.critical(f'!!! Bot thread crashed: {e} !!!', exc_info=True)
    finally:
        # Clean up state when the bot stops for any reason
        _bot_instance = None


@router.post("/activate")
async def activate_bot():
    global _bot_thread
    if (_bot_instance and _bot_instance.is_ready()) or (_bot_thread and _bot_thread.is_alive()):
        raise HTTPException(status_code=400, detail="Bot is already active or starting.")
    
    logging.info("Bot activation requested via API.")
    _bot_thread = threading.Thread(target=_run_bot_in_thread, daemon=True)
    _bot_thread.start()
    return {"success": True, "message": "Bot activation initiated."}


@router.post("/deactivate")
async def deactivate_bot():
    if not _bot_instance or not _bot_instance.is_ready():
        raise HTTPException(status_code=400, detail="Bot is not running.")
    
    try:
        logging.info("--- Sending shutdown signal to bot via API... ---")
        # Use run_coroutine_threadsafe to safely call the async close method
        # from this synchronous thread context.
        future = asyncio.run_coroutine_threadsafe(_bot_instance.close(), _bot_instance.loop)
        future.result(timeout=10) # Wait for the close operation to complete
        return {"success": True, "message": "Bot deactivation initiated."}
    except Exception as e:
        logging.error(f"Error during bot deactivation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def check_bot_status():
    if _bot_instance and _bot_instance.is_ready():
        return {"status": "active"}
    elif _bot_thread and _bot_thread.is_alive():
        return {"status": "starting"}
    else:
        return {"status": "inactive"}


@router.get("/invite")
async def get_discord_invite():
    if _bot_instance and _bot_instance.invite_link:
        return {"status": "active", "invite": _bot_instance.invite_link}
    else:
        return {"status": "inactive", "message": "Bot is not running or invite link is not yet available."}


@router.get("/stream-logs")
async def stream_logs(request: Request):
    """Streams the contents of the bot's log file using Server-Sent Events."""
    
    async def log_generator():
        try:
            with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
                # Go to the end of the file
                f.seek(0, 2)
                while True:
                    if await request.is_disconnected():
                        logging.info("Client disconnected from log stream.")
                        break

                    line = f.readline()
                    if not line:
                        # No new line, wait a bit
                        await asyncio.sleep(0.5)
                        continue
                    
                    # SSE format: "data: <your message>\n\n"
                    yield f"data: {line.strip()}\n\n"
        except FileNotFoundError:
            yield f"data: Log file not found. It will be created when the bot is started.\n\n"
        except Exception as e:
            logging.error(f"Error in log streamer: {e}")
            yield f"data: An error occurred while streaming logs: {e}\n\n"

    return StreamingResponse(log_generator(), media_type="text/event-stream")