# main.py
"""Main FastAPI application entry point."""

import argparse
import os
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from api.routers import characters, servers, config, discord
import tracemalloc

# Start tracing memory allocations
#tracemalloc.start()
# Create the FastAPI app
app = FastAPI(
    title="Configuration Manager API", 
    description="API for managing character, channel, and bot configurations"
)

# Set up static files
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

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

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    file_path = os.path.join(os.path.dirname(__file__), "favicon.ico")
    return FileResponse(file_path, media_type="image/x-icon")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run FastAPI app with configurable options 🚀"
    )
    
    parser.add_argument(
        "--host",
        choices=["127.0.0.1", "0.0.0.0", "localhost"],
        default="127.0.0.1",
        help="Host to bind the server (default: 127.0.0.1)"
    )

    parser.add_argument(
        "--port",
        type=int,
        choices=[5000, 5666, 8000, 8080, 9000],
        default=5666,
        help="Port to run the server on (default: 5666)"
    )

    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )

    args = parser.parse_args()

    uvicorn.run("main:app", host=args.host, port=args.port, reload=args.reload)
