from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
import threading
import asyncio
import time
from typing import Dict, Optional, Any

# Import your Discord bot modules
import discord
import src.data.config_data as config
# Create FastAPI app
app = FastAPI(title="Discord Bot Control API")

# Track bot state
bot_state = {
    "active": False,
    "start_time": None,
    "discord_client": None,
    "thread": None
}

# Response models
class BotStatus(BaseModel):
    active: bool
    uptime_seconds: Optional[float] = None
    start_time: Optional[float] = None
    
class ActivationResponse(BaseModel):
    success: bool
    message: str
    status: BotStatus

# Function to run Discord bot in a separate thread
def run_discord_bot():
    # Use your existing Discord token and setup code
    
    discord_token = config.get_key()
    
    if discord_token is None:
        raise RuntimeError("Discord token is not set in config!")
    
    intents = discord.Intents.all()
    intents.message_content = True
    client = discord.Client(intents=intents)
    
    # Set up your existing event handlers and commands
    # This would be where you'd include all your existing setup
    # Including your on_ready, on_message handlers, etc.
    
    # Store client for later access
    bot_state["discord_client"] = client
    
    # Record start time
    bot_state["start_time"] = time.time()
    bot_state["active"] = True
    
    # Run the bot
    client.run(discord_token)
    
    # When the bot stops
    bot_state["active"] = False
    bot_state["start_time"] = None

@app.post("/bot/activate", response_model=ActivationResponse)
async def activate_bot():
    if bot_state["active"]:
        return ActivationResponse(
            success=False,
            message="Bot is already running",
            status=BotStatus(
                active=True,
                uptime_seconds=time.time() - bot_state["start_time"],
                start_time=bot_state["start_time"]
            )
        )
    
    try:
        # Start bot in a separate thread
        bot_thread = threading.Thread(target=run_discord_bot)
        bot_thread.daemon = True
        bot_thread.start()
        
        # Store thread for later access
        bot_state["thread"] = bot_thread
        
        # Give it a moment to start
        await asyncio.sleep(2)
        
        if bot_state["active"]:
            return ActivationResponse(
                success=True,
                message="Bot successfully activated",
                status=BotStatus(
                    active=True,
                    uptime_seconds=time.time() - bot_state["start_time"],
                    start_time=bot_state["start_time"]
                )
            )
        else:
            return ActivationResponse(
                success=False,
                message="Bot failed to activate",
                status=BotStatus(active=False)
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to activate bot: {str(e)}"
        )

@app.post("/bot/deactivate", response_model=ActivationResponse)
async def deactivate_bot():
    if not bot_state["active"]:
        return ActivationResponse(
            success=False,
            message="Bot is not currently running",
            status=BotStatus(active=False)
        )
    
    try:
        # Close the Discord client
        if bot_state["discord_client"]:
            await bot_state["discord_client"].close()
        
        # Give it a moment to shut down
        await asyncio.sleep(2)
        
        # Update state
        bot_state["active"] = False
        uptime = time.time() - bot_state["start_time"] if bot_state["start_time"] else 0
        start_time = bot_state["start_time"]
        bot_state["start_time"] = None
        bot_state["discord_client"] = None
        bot_state["thread"] = None
        
        return ActivationResponse(
            success=True,
            message="Bot successfully deactivated",
            status=BotStatus(
                active=False,
                uptime_seconds=uptime,
                start_time=start_time
            )
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to deactivate bot: {str(e)}"
        )

@app.get("/bot/status", response_model=BotStatus)
async def get_bot_status():
    if bot_state["active"] and bot_state["start_time"]:
        return BotStatus(
            active=True,
            uptime_seconds=time.time() - bot_state["start_time"],
            start_time=bot_state["start_time"]
        )
    else:
        return BotStatus(active=False)

# Run the API with: uvicorn main:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)