import copy
import discord
from jinja2 import Environment

# Adjust these import paths to match your project structure
from src.models.aicharacter import ActiveCharacter
from src.models.dimension import ActiveChannel
from src.plugins.manager import PluginManager
from src.controller.history import get_history 
from api.db.database import Database

# --- A sensible default template ---
# This template will be saved to the database if it doesn't exist.
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
</instruction>
"""
# Note: The '{{- ... -}}' syntax in Jinja2 removes leading whitespace for cleaner output.


class PromptEngineer:
    def __init__(self, bot: ActiveCharacter, message: discord.Message, channel: ActiveChannel,plugin_manager:PluginManager):
        self.bot = bot
        self.user_name = str(message.author.display_name)
        self.message = message
        self.channel = channel
        
        # Get the database instance from one of the active models
        self.db: Database = bot.db
        
        self.plugin_manager = plugin_manager 
        self.jinja_env = Environment(trim_blocks=True, lstrip_blocks=True) # Recommended settings for prompt templates

        self.stopping_strings = ["[System", "(System", self.user_name + ":", "[End", "</", "<|end of sentence|>"]

    def get_template_from_preset(self) -> str:
        """
        Retrieves the 'Default' preset template from the database.
        If the preset does not exist, it creates it with a default template
        and then returns it.
        """
        DEFAULT_PRESET_NAME = "Default"
        
        try:
            preset = self.db.get_preset(name=DEFAULT_PRESET_NAME)

            if not preset:
                # The preset does not exist, so we create it.
                print(f"Preset '{DEFAULT_PRESET_NAME}' not found. Creating it in the database...")
                self.db.create_preset(
                    name=DEFAULT_PRESET_NAME,
                    description="The default system prompt template, used as a fallback.",
                    prompt_template=DEFAULT_PROMPT_TEMPLATE
                )
                # Return the default template string we just saved
                return DEFAULT_PROMPT_TEMPLATE
            else:
                # The preset exists, return its template.
                # Provide a fallback to the default constant just in case the DB entry is empty.
                return preset.get('prompt_template') or DEFAULT_PROMPT_TEMPLATE

        except Exception as e:
            # If any database error occurs, log it and fall back to the default template
            print(f"Error accessing database for presets: {e}. Falling back to default template.")
            return DEFAULT_PROMPT_TEMPLATE

    async def create_prompt(self) -> str:
        """
        Gathers context, pre-renders nested templates in character data,
        and then renders the final prompt string.
        """
        history = await get_history(self.message.channel, self.db)

        # --- STEP 1: Create a context for the INNER templates ---
        # This context will be used to render strings like the character's persona.
        # Your idea to add 'char' was perfect for this.
        inner_context = {
            "char": self.bot.name,
            "user": self.user_name
        }

        # --- STEP 2: Pre-render the character's data ---
        # We create a deep copy to avoid modifying the original bot object.
        rendered_character = copy.deepcopy(self.bot)
        
        # Render any fields that might contain Jinja templates
        if rendered_character.persona:
            template = self.jinja_env.from_string(rendered_character.persona)
            rendered_character.persona = template.render(inner_context)

        if rendered_character.examples:
            # Create a new list to hold the rendered examples
            rendered_examples = []
            # Loop through each example string in the list
            for example_string in rendered_character.examples:
                # Treat each string as a template and render it
                template = self.jinja_env.from_string(example_string)
                rendered_examples.append(template.render(inner_context))
            # Replace the old list with the new list of rendered strings
            rendered_character.examples = rendered_examples
            
        if rendered_character.instructions:
            template = self.jinja_env.from_string(rendered_character.instructions)
            rendered_character.instructions = template.render(inner_context)

        # --- STEP 3: Create the context for the MAIN template ---
        # This now uses our pre-rendered character object.
        base_context = {
            "character": rendered_character, # <-- Using the rendered version!
            "channel": self.channel,
            "user": self.user_name,
            "history": history,
            "message": self.message
        }

        # 2. Execute plugins based on the message content
        plugin_outputs = await self.plugin_manager.scan_and_execute(
            self.message, self.bot, self.channel, self.db
        )
        
        final_context = {**base_context, "plugins": plugin_outputs}

        # --- STEP 5: Final Render ---
        prompt_template_str = self.get_template_from_preset()
        template = self.jinja_env.from_string(prompt_template_str)
        final_prompt = template.render(final_context)
        #print(f"=====================\nFINAL PROMPT\n=======================\n{final_prompt}")
        
        return final_prompt
       