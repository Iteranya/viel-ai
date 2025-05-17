from openai import OpenAI
from src.models.queue import QueueItem
from src.models.prompts import PromptEngineer
from src.data.config_data import load_or_create_config,Config,get_key
import re
async def generate_response(task:QueueItem):

    ai_config:Config = load_or_create_config()

    client = OpenAI(
        base_url=ai_config.ai_endpoint,
        api_key= get_key(),
        )
    user_message = clean_string(task.message.content)
    
    completion = client.chat.completions.create(
    model=ai_config.base_llm,
    stop=task.stop,
    temperature=ai_config.temperature, # I forgor :3
    
    messages=[
        {
        "role":"system",
        "content":f"<context> {task.prompt} </context>"
        },
        {
        "role": "user",
        "content": f"[Reply] {user_message} [End]"
        },
        {
        "role": "assistant",
        "content": task.prefill
        }
    ]
    )
    result = completion.choices[0].message.content
    
    task.result = result
    return task

def clean_string(s):
    # Matches only if the string starts with a single word (no spaces), followed by ':'
    return re.sub(r'^[^\s:]+:\s*', '', s) if re.match(r'^[^\s:]+:\s*', s) else s
