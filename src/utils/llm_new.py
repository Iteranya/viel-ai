from openai import OpenAI
from src.models.queue import QueueItem
from src.models.prompts import PromptEngineer
from src.data.config_data import load_or_create_config,Config,get_key

async def generate_response(task:QueueItem):

    ai_config:Config = load_or_create_config()

    client = OpenAI(
        base_url=ai_config.ai_endpoint,
        api_key= get_key(),
        )
    
    completion = client.chat.completions.create(
    model=ai_config.base_llm,
    stop=task.stop,
    messages=[
        {
        "role": "user",
        "content": task.prompt
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