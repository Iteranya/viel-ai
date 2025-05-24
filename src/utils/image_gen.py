import discord
from src.data.config_data import load_or_create_config,Config,get_key
from openai import OpenAI
import re

async def generate_sd_prompt(message = discord.message.Message):
    print("Trying to Generate Prompt")
    ai_config:Config = load_or_create_config()

    client = OpenAI(
        base_url=ai_config.ai_endpoint,
        api_key= get_key(),
        )

    content = message.content
    print(f"Generating SD Prompt~\n\n Prompt: {content}")
    
    completion = client.chat.completions.create(
    model=ai_config.base_llm,
    messages=[
        {
        "role": "system",
        "content": "Your task is to create AI Image Gen In This Exact Format:\n\nGeneral description: A lengthy description of the whole image here.\n\nPrompt:\n- Gender(1girl/2girls/1boy/1other/3boys)\n- Rating(Safe/Sensitive/Explicit/NSFW)\n- Camera(From front/dutch angle)\n- Physical(Blue hair/red eyes/petite/long hair/cat ears)\n- Act(Standing, Sitting, Masturbating, etc)\n- Clothing(Blue shirt/red tie/glasses)\n- Background(Classroom/Room/Alleyway)\n- Enhance(masterpiece/high score/absurdres, anime screen cap)\n\nAvoid using too specific term like: \"Nazarick, Scarlet Devil Mansion\" as the image generation AI rarely knows that sort of specific term, but character name is permitted. Also write down all sorts of general items that paints the scene or list of visual items that describes a character.\n\nThis also includes costumes and character appearances. Longer prompt is better.\n\nNote: You must write down in terms of danbooru tags/keyword. Do not write down (jet black waist-length hair) instead write down (black hair, medium hair). Remember, the AI only understands keyword, not description. \n\nExample:\n\n{{user}}:  Draw me hatsune miku, sitting in an arcade\n{{char}}: General Description: The arcade hums with neon life as the camera catches Miku from a low side angle, her turquoise pigtails swaying slightly as she leans forward on the stool. The glow of fighting game screens paints her face in shifting blues and pinks, fingers hovering over the arcade buttons with playful anticipation. Her thigh-highs press against the cabinet’s edge, the teal accents of her dress catching the artificial light like shallow water. Behind her, the blur of other players and pixelated explosions frame the scene—a digital idol momentarily lost in the thrill of the game.\nPrompt: \n- Gender: (1girl)\n- Rating: (Safe)\n- Camera: (from side, slight low angle)\n- Physical: (blue hair, twin tails, blue eyes, green eyes)\n- Act: (sitting, sitting on chair, leaning forward, excited)\n- Clothing: (sleeveless white and teal dress, thigh-highs, fingerless gloves)\n- Background: (neon-lit arcade, colorful game screens in background, soft glow)\n- Enhance: (masterpiece, high score, absurdres, anime screen cap)\n\nYOU MUST FORMAT PROMPT BETWEEN ( )  and DO NOT PUT DESCRIPTION BETWEEN  ( )\n\nUnderstand that sometimes user will make nonsensical queries. Your job if that happens is to get creative. But remember, the AI is only limited to draw anime girls and danbooru tags. If user specifically ask for  NSFW, add extra keywords and focus on character appearance."
        },
        {
        "role": "user",
        "content": f"Create an image of {content}"
        },
        {
        "role": "assistant",
        "content": "Understood, here's the requested prompt: \n\nGeneral Description:"
        }
    ]
    )
    result = completion.choices[0].message.content
    print(result)
    return format_prompt(result)

def format_prompt(text:str):
    """
    Transform a structured text description into a weighted prompt string.
    
    Args:
        text (str): Input text with sections like General Description, Gender, Rating, etc.
        
    Returns:
        str: Formatted string with comma-separated weighted terms
    """
    # Define the weight mapping
    weight_mapping = {
        "Gender": 1.0,
        "Rating": 0.0,
        "Camera": 1.0,
        "Physical": 0.75,
        "Act": 0.4,
        "Clothing": 0.85,
        "Background": 0.35,
        "Enhance": 0.5
    }
    
    # Initialize the result list
    result_terms = []
    
    # Extract the sections from the text
    for section, weight in weight_mapping.items():
        # Find the section in the text
        section_pattern = f"{section}: "
        if section_pattern in text:
            # Get the content after the section label
            start_idx = text.find(section_pattern) + len(section_pattern)
            end_idx = text.find("\n-", start_idx)
            if end_idx == -1:  # If this is the last section
                end_idx = text.find("\n", start_idx)
                if end_idx == -1:  # If there's no newline after this section
                    end_idx = len(text)
            
            content = text[start_idx:end_idx].strip()
            
            # Remove parentheses if present
            content = content.replace("(", "").replace(")", "")
            
            # Split by commas or spaces (if no commas)
            if "," in content:
                items = [item.strip() for item in content.split(",")]
            else:
                items = [content.strip()]
            
            # Add each item with its weight to the result
            for item in items:
                if item:  # Skip empty items
                    result_terms.append(item)
    
    # Join all terms with commas
    result_string = ", ".join(result_terms)
    
    return result_string
