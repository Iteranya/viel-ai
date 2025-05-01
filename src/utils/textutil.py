import re

def clean_text(text:str):
    """
    Remove emojis, trailing whitespace, line breaks, and bracket-like characters from a given string.
    
    Args:
        text (str): Input string that may contain emojis, whitespace, line breaks, and trailing characters
    
    Returns:
        str: Cleaned string 
    """
    # Emoji pattern
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        "]+", flags=re.UNICODE)
    
    # Remove trailing whitespace and line breaks first
    text = text.rstrip()
    
    # Remove emojis
    text_without_emoji = emoji_pattern.sub(r'', text)
    
    # Remove trailing bracket-like characters, with more inclusive matching
    cleaned_text = re.sub(r'[)\]>:;,\s]+$', '', text_without_emoji)
    
    return cleaned_text.rstrip()

def remove_last_word_before_final_colon(text: str) -> str:
    # Define the regex pattern to find the last word before the final colon
    pattern = r'\b\w+\s*:$'
    
    # Use re.sub to replace the matched pattern with an empty string
    result = re.sub(pattern, '', text)
    
    return result.strip()  # Remove any leading or trailing whitespace

def remove_string_before_final(data: str) -> str:
    substrings = ["[/","[System", "[SYSTEM", "[Reply", "[REPLY", "(System", "(SYSTEM","[End]","[End"]
    
    for substr in substrings:
        if data.endswith(substr):
            return data[:-len(substr)]
    
    return data

def remove_fluff(text: str) -> str:
    # Find the last pair of asterisks and the content between them
    pattern = r'\*(.*?)\*'
    
    # Use re.findall to get all matches and re.sub to remove the last one
    matches = re.findall(pattern, text)
    if matches:
        # Get the last match and construct the regex to remove it
        last_fluff = re.escape(f"*{matches[-1]}*")
        text = re.sub(last_fluff, '', text, count=1)
    
    return text.strip()  # Remove any extra whitespace

def clean_links(text):
    
    # Remove common tracking parameters
    tracking_params = [
        'utm_source', 'utm_medium', 'utm_campaign', 'utm_term', 'utm_content', 
        'fbclid', 'gclid', 'ref', 'referrer', 'ref_url', 'ref_src'
    ]
    
    def clean_single_link(url):
        # Remove duplicate protocols
        url = re.sub(r'^(https?://)(https?://)', r'\1', url)
        
        # Remove tracking parameters
        for param in tracking_params:
            url = re.sub(rf'([?&]){param}=[^&]*&?', r'\1', url)
        
        # Remove trailing '?' or '&' if left after parameter removal
        url = re.sub(r'[?&]$', '', url)
        
        # Remove 'www.' prefix
        url = re.sub(r'^(https?://)(www\.)', r'\1', url)
        
        # Remove trailing slash for non-directory URLs
        if url.count('/') <= 3:  # Keeps slashes for deeper paths
            url = url.rstrip('/')
        
        return url
    
    # Find and clean URLs in the text
    def replace_urls(match):
        return clean_single_link(match.group(0))
    
    # Regex to match URLs
    url_pattern = r'https?://\S+'
    cleaned_text = re.sub(url_pattern, replace_urls, text)
    
    return cleaned_text
