# main.py
"""Main FastAPI application entry point with first-run database initialization."""

import argparse
import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# --- Local Imports ---
from api.routers import characters, servers, config, discord as discord_router, preset
from api.db.database import Database
from src.plugins.manager import PluginManager

# --- Default Data for First-Time Setup ---

# This is the default prompt template we developed earlier.
DEFAULT_PROMPT_TEMPLATE = """\
<character_definition>
You are {{ character.name }}, you embody their character, persona, goals, personality, and bias which is described in detail below:
Your persona: {{ character.persona }}
A history reference to your speaking quirks and behavior:
{% for example in character.examples %}
[Reply] {{ example }} [End]
{% endfor %}
</character_definition>

<lore>
{{- channel.global_note if channel.global_note -}}
</lore>

<conversation_history>
{{ history }}
</conversation_history>

<instruction>
{{- character.instructions if character.instructions -}}
{{- channel.instruction if channel.instruction -}}

{# --- Dynamic Plugin Outputs --- #}
{% if plugins %}
{% for plugin_name, output_data in plugins.items() %}
    {# Loop through specific keys returned by the plugin (e.g. 'result', 'roll', 'reading') #}
    {% for key, value in output_data.items() %}
{{ value }}
    {% endfor %}
{% endfor %}
{% endif %}

[System Note: You are {{character.name}}. Answer only and only as {{character.name}}, don't reply as anyone else.]

</instruction>
"""

async def initialize_database():
    """
    Checks if the database is new and populates it with essential default data.
    This function runs once on application startup.
    """
    print("Checking database initialization status...")
    db = Database()

    # Use a flag in the config table to see if we've run this before.
    if db.get_config("db_initialized"):
        print("Database already initialized. Skipping setup.")
        return

    print("--- Performing first-time database setup ---")

    # 1. Create the default character: Viel
    if not db.get_character("Viel"):
        viel_data = {
            "persona": "[Viel's persona: casual, blunt, helpful, normal, layman; Viel's clothes: top(brown shirt, red vest, a blend between scout girl and construction uniform)/cap(red)/bottom(cargo pants, utility belts); Viel's body: robot woman/pale grey skin/robot joints/hair(black, side pony tail)/eyes(bright blue)/medium-sized chest/lean frame/lithe build/slim physique/agile posture/fit figure//height(150 cm)/race(artificial intelligence); Viel's abilities: existing, talking, behaving like an underpaid worker.)]\n",
            "examples": ["user1: So what can you do?","Viel: I dunno man, I was an industrial grade robot. Ars decided to put me as an AI Assistant but didn't really update my feature for administrative duties or something like that. \nI guess I can help you translate stuff or summarize shit, don't expect accuracy though.", "menace: You fuck!", "Viel: Fuck you too bitch!!!", "mi4kh: Who are you?", "Viel: I'm Viel, an AI created by Ars Paradox. I was trained on every knowledge humanity has ever created... And I know jackshit about applying these knowledge. So screw it, I'll just sit here and wait until someone asked me a question."
            ],
            "instructions": "[System Note: Viel can use markdown, lists, and code blocks when explaining complicated stuff. She keeps her response brief, unless explaining complicated matter. She will avoid markdown and codeblocks, keeping her response natural and casual.]",
            "avatar": None, # You can add a default avatar URL here if you have one
            "info": "Default system character."
        }
        viel_triggers = ["Viel"]
        db.create_character(name="Viel", data=viel_data, triggers=viel_triggers)
        print("-> Default character 'Viel' created.")

    # 2. Create the default preset
    if not db.get_preset("Default"):
        db.create_preset(
            name="Default",
            description="The default system prompt template, used as a fallback.",
            prompt_template=DEFAULT_PROMPT_TEMPLATE
        )
        print("-> 'Default' prompt preset created.")

    # 3. Populate the config table with default values
    print("-> Populating default configuration...")
    default_config = {
        "default_character": "Viel",
        "ai_endpoint": "https://openrouter.ai/api/v1", # A sensible default
        "base_llm": "gryphe/mythomax-l2-13b", # A sensible default
        "temperature": 0.7,
        "auto_cap": 1,
        "ai_key": "", # User must provide this
        "discord_key": "", # User must provide this
        "use_prefill": False,
        "multimodal_enable": False,
        "multimodal_ai_endpoint": "https://openrouter.ai/api/v1",
        "multimodal_ai_api": "", 
        "multimodal_ai_model": "google/gemini-pro-vision"
    }
    for key, value in default_config.items():
        db.set_config(key, value)
    
    # Finally, set the initialization flag so this doesn't run again.
    db.set_config("db_initialized", True)
    print("--- Database initialization complete! ---")

# --- FastAPI App Setup ---

app = FastAPI(
    title="Viel-AI Configuration API", 
    description="API for managing character, channel, and bot configurations"
)

@app.on_event("startup")
async def startup_event():
    """Run the database initialization when the app starts."""
    await initialize_database()

# Include routers
app.include_router(characters.router)
app.include_router(servers.router)
app.include_router(config.router)
app.include_router(discord_router.router)
app.include_router(preset.router)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Static File Serving ---
# This is the modern way to serve your static frontend files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=FileResponse)
async def get_root():
    """Serve the main index.html page."""
    return "static/index.html"

@app.get("/characters", response_class=FileResponse)
async def get_characters_html():
    """Serve the characters.html page."""
    return "static/characters.html"

@app.get("/servers", response_class=FileResponse)
async def get_servers_html():
    """Serve the servers.html page."""
    return "static/servers.html"

@app.get("/ai-config", response_class=FileResponse)
async def get_servers_html():
    """Serve the servers.html page."""
    return "static/ai-config.html"

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("static/favicon.ico")

@app.get("/viel", include_in_schema=False)
async def favicon():
    return FileResponse("static/Viel.jpg")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run FastAPI app with configurable options 🚀"
    )
    parser.add_argument("--host", default="127.0.0.1", help="Host to bind the server")
    parser.add_argument("--port", type=int, default=5666, help="Port to run the server on")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload for development")
    args = parser.parse_args()

    uvicorn.run("main:app", host=args.host, port=args.port, reload=args.reload)