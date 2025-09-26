from openai import AsyncOpenAI
from src.models.queue import QueueItem
from src.data.config_data import load_or_create_config,Config,get_key
import re
import traceback
from src.models.aicharacter import AICharacter

async def generate_response(task: QueueItem):
    try:
        ai_config: Config = load_or_create_config()
        client = AsyncOpenAI(
            base_url=ai_config.ai_endpoint,
            api_key=get_key(),
        )
        user_message = clean_string(task.message.content)
        if task.plugin:
            user_message = f"[System Note: {task.plugin}]\n{user_message}"
        completion = await client.chat.completions.create(
            model=ai_config.base_llm,
            stop=task.stop,
            temperature=ai_config.temperature,
            messages=[
                {
                    "role": "system",
                    "content": f"<context> {task.prompt} </context>"
                },
                {
                    "role": "user",
                    "content": f"[Reply] {user_message} [End]"
                }
                # {
                #     "role": "assistant",
                #     "content": task.prefill
                # }
            ]
        )
        result = completion.choices[0].message.content if completion.choices else f"//[OOC: Sorry, the AI broke on my end, can you check the log? Thanks]"
        result = result.replace("[Reply]","")
        result = result.replace(f"{task.bot}:","")
        result = clean_thonk(result)
        # print(completion)
        task.result = result
    except Exception as e:
        # Comprehensive error handling
        error_type = type(e).__name__
        error_message = str(e)
        error_traceback = traceback.format_exc()
        
        # Log the full error for debugging
        print(f"Error in generate_response: {error_type}: {error_message}\n{error_traceback}")
        
        # Create a detailed error message
        detailed_error = f"//[OOC: AI Error - {error_type}]\n"
        
        # Handle specific OpenAI errors
        if hasattr(e, 'status_code'):
            detailed_error += f"Status Code: {e.status_code}\n"
        
        if hasattr(e, 'response') and e.response:
            detailed_error += f"Response: {e.response}\n"
        
        # Add context about what was being processed
        try:
            detailed_error += f"Task ID: {getattr(task, 'id', 'Unknown')}\n"
            detailed_error += f"Model: {getattr(ai_config, 'base_llm', 'Unknown')}\n"
            detailed_error += f"Message Length: {len(getattr(task.message, 'content', ''))}\n"
        except:
            detailed_error += "Unable to retrieve task context\n"
        
        detailed_error += f"Error Details: {error_message}\n"
        detailed_error += f"Full Traceback:\n{error_traceback}"
        
        task.result = detailed_error
    return task

def clean_string(s):
    # Matches only if the string starts with a single word (no spaces), followed by ':'
    return re.sub(r'^[^\s:]+:\s*', '', s) if re.match(r'^[^\s:]+:\s*', s) else s

def clean_thonk(s):
    # Find </think> and remove everything before it (including </think>)
    match = re.search(r'</think>', s)
    if match:
        # Recursively clean the remaining string
        return clean_thonk(s[match.end():])
    else:
        return s

async def generate_blank(system,user):
    try:
        ai_config: Config = load_or_create_config()

        client = AsyncOpenAI(
            base_url=ai_config.ai_endpoint,
            api_key=get_key(),
        )

        completion = await client.chat.completions.create(
            model=ai_config.base_llm,
            temperature=ai_config.temperature,
            messages=[
                {
                    "role": "system",
                    "content": system
                },
                {
                    "role": "user",
                    "content":user
                }
            ]
        )

        result = completion.choices[0].message.content if completion.choices else f"//[Error]"
        result = clean_thonk(result)
    except Exception as e:
        result = str(e)
    return result

async def generate_in_character(system,user,assistant):
    config = load_or_create_config()
    bot = AICharacter(config.default_character)
    char_prompt = await bot.get_character_prompt()
    system_prompt = char_prompt + system

    try:
        ai_config: Config = load_or_create_config()

        client = AsyncOpenAI(
            base_url=ai_config.ai_endpoint,
            api_key=get_key(),
        )

        completion = await client.chat.completions.create(
            model=ai_config.base_llm,
            temperature=ai_config.temperature,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content":user
                },
                {
                    "role": "assistant",
                    "content": assistant
                }
            ]
        )

        result = completion.choices[0].message.content if completion.choices else f"//[Error]"
        result = clean_thonk(result)
    except Exception as e:
        result = str(e)
    return result
