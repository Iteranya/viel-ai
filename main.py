# main.py
"""Main FastAPI application entry point."""

import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from api.routers import characters, servers, config, discord

# Create the FastAPI app
app = FastAPI(
    title="Configuration Manager API", 
    description="API for managing character, channel, and bot configurations"
)

# Set up static files
# app.mount("/interface", StaticFiles(directory="interface"), name="interface")

# Include routers
app.include_router(characters.router)
app.include_router(servers.router)
app.include_router(config.router)
app.include_router(discord.router)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def get_html():
    """Serve the main HTML page."""
    template_path = "index.html"
    with open(template_path, "r") as f:
        html = f.read()
    return html

# @app.get("/admin", response_class=HTMLResponse)
# async def get_new_interface():
#     """Serve the new interface HTML page."""
#     template_path = "interface/index.html"
#     with open(template_path, "r") as f:
#         html = f.read()
#     return html

# @app.get("/admin/characters", response_class=HTMLResponse)
# async def get_new_interface():
#     """Serve the new interface HTML page."""
#     template_path = "interface/characters.html"
#     with open(template_path, "r") as f:
#         html = f.read()
#     return html

# @app.get("/admin/config", response_class=HTMLResponse)
# async def get_new_interface():
#     """Serve the new interface HTML page."""
#     template_path = "interface/config.html"
#     with open(template_path, "r") as f:
#         html = f.read()
#     return html

# @app.get("/admin/servers", response_class=HTMLResponse)
# async def get_new_interface():
#     """Serve the new interface HTML page."""
#     template_path = "interface/server-channels.html"
#     with open(template_path, "r") as f:
#         html = f.read()
#     return html

# Main entry point
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5666)