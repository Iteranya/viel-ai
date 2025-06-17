
import re
from src.utils.llm_new import generate_in_character
from src.controller.plugin_registry import plugin

@plugin
async def summarize(content: str):
    """
    Summarizes the given text content or search result into a concise, markdown-friendly snippet highlighting only the core information.

    This asynchronous function uses a prompt-based approach to guide a language model (presumably via `generate_blank`)
    into producing a well-formatted summary wrapped in <summary> tags. The summary is extracted and returned as plain text.

    Parameters:
        content (str): The full text content that needs to be summarized.

    Returns:
        str: A condensed summary extracted from within <summary> tags, or the full model response if the tags aren't found.

    Example:
        summary = await summarize("Here is a long article about space and black holes...")
        print(summary)
        # Might print: "Black holes are regions in space with gravitational pulls so strong not even light escapes."
    """
    result: str
    summary_prompt = (
        "You are an absolute expert at summarizing content and a markdown whisperer. "
        "You can condense any information into easy-to-digest snippets of information without losing the core information. "
        "In fact, you will instead highlight the core information required. "
        "Write down the summary within <summary></summary>."
    )
    assistant_prompt = "Understood, here is the summary of the given text between <summary>  </summary>"
    user_prompt = f"Please summarize the following text: <text>{content}</text>"
    
    response = await generate_in_character(summary_prompt, user_prompt, assistant_prompt)

    # Pull out the juicy core summary wrapped in <summary> tags
    match = re.search(r"<summary>(.*?)</summary>", response, re.DOTALL)
    result = match.group(1).strip() if match else response

    return result
