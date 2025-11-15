# api_router.py

from collections import deque
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
from api.bot_state import bot_state

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
        bot_state.bot_instance = Viel(intents=intents)
        bot_state.bot_instance.run()
        logging.info("--- Bot has shut down cleanly. ---")
    except Exception as e:
        logging.critical(f'!!! Bot thread crashed: {e} !!!', exc_info=True)
    finally:
        # Clean up state when the bot stops for any reason
        _bot_instance = None


@router.post("/activate")
async def activate_bot():
    # --- CHANGE THIS ---
    # Check the shared state object
    if (bot_state.bot_instance and bot_state.bot_instance.is_ready()) or (bot_state.bot_thread and bot_state.bot_thread.is_alive()):
        raise HTTPException(status_code=400, detail="Bot is already active or starting.")
    
    logging.info("Bot activation requested via API.")
    # --- CHANGE THIS ---
    bot_state.bot_thread = threading.Thread(target=_run_bot_in_thread, daemon=True)
    bot_state.bot_thread.start()
    return {"success": True, "message": "Bot activation initiated."}


@router.post("/deactivate")
async def deactivate_bot():
    # --- CHANGE THIS ---
    if not bot_state.bot_instance or not bot_state.bot_instance.is_ready():
        raise HTTPException(status_code=400, detail="Bot is not running.")
    
    try:
        logging.info("--- Sending shutdown signal to bot via API... ---")
        # --- CHANGE THIS ---
        future = asyncio.run_coroutine_threadsafe(bot_state.bot_instance.close(), bot_state.bot_instance.loop)
        future.result(timeout=10)
        return {"success": True, "message": "Bot deactivation initiated."}
    except Exception as e:
        logging.error(f"Error during bot deactivation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def check_bot_status():
    # --- CHANGE THIS ---
    if bot_state.bot_instance and bot_state.bot_instance.is_ready():
        return {"status": "active"}
    elif bot_state.bot_thread and bot_state.bot_thread.is_alive():
        return {"status": "starting"}
    else:
        return {"status": "inactive"}


@router.get("/invite")
async def get_discord_invite():
    # --- CHANGE THIS ---
    if bot_state.bot_instance and bot_state.bot_instance.invite_link:
        return {"status": "active", "invite": bot_state.bot_instance.invite_link}
    else:
        return {"status": "inactive", "message": "Bot is not running or invite link is not yet available."}


@router.get("/stream-logs")
async def stream_logs(request: Request):
    """
    Streams the bot's log file using Server-Sent Events.
    Starts with the last 10 lines of the file and then continues to
    stream new lines as they are added.
    """

    async def log_generator():
        try:
            with open(LOG_FILE_PATH, 'r', encoding='utf-8') as f:
                # 1. Use deque to efficiently get the last 10 lines.
                # This reads the whole file but only keeps the last 10 lines in memory.
                # After this, the file pointer 'f' will be at the end of the file.
                last_lines = deque(f, maxlen=10)

                # 2. Send the initial batch of last lines to the client.
                for line in last_lines:
                    if line.strip():  # Avoid sending empty lines
                        yield f"data: {line.strip()}\n\n"

                # 3. Now, start tailing the file for new lines.
                # The file pointer is already at the end, so this works perfectly.
                while True:
                    if await request.is_disconnected():
                        logging.info("Client disconnected from log stream.")
                        break

                    line = f.readline()
                    if not line:
                        # No new line, wait a bit before checking again.
                        await asyncio.sleep(0.5)
                        continue

                    # Send any new line to the client.
                    yield f"data: {line.strip()}\n\n"

        except FileNotFoundError:
            yield f"data: Log file not found. It will be created when the bot is started.\n\n"
        except Exception as e:
            logging.error(f"Error in log streamer: {e}")
            yield f"data: An error occurred while streaming logs: {e}\n\n"

    return StreamingResponse(log_generator(), media_type="text/event-stream")