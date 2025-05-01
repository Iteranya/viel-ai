from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re
from urllib.parse import urlparse, parse_qs

def contains_youtube_link(text):
    """
    Checks if a string contains a YouTube video link.

    Args:
        text: The string to check.

    Returns:
        True if the string contains a YouTube link, False otherwise.
    """
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|shorts/|/)([a-zA-Z0-9_-]{11})'
    )
    youtube_match = re.search(youtube_regex, text)

    if youtube_match:
        return True
    return False

def extract_video_id(text_with_url):
    """
    Extracts the YouTube video ID from a string containing a URL.
    
    Args:
        text_with_url: The string containing the YouTube video URL.
        
    Returns:
        The video ID if found, None otherwise.
    """
    # Extract YouTube URL using regex
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|shorts/|/)([a-zA-Z0-9_-]{11})'
    )
    youtube_match = re.search(youtube_regex, text_with_url)

    short_youtube_regex = r"(https?://)?(www\.)?youtu\.be/([a-zA-Z0-9_-]{11})"
    short_youtube_match = re.search(short_youtube_regex, text_with_url)

    if youtube_match:
        video_url = youtube_match.group(0)
    elif short_youtube_match:
        video_url = short_youtube_match.group(0)
    else:
        return None

    # Extract video ID from URL
    parsed_url = urlparse(video_url)
    query_params = parse_qs(parsed_url.query)
    video_id = query_params.get("v", [None])[0]

    if not video_id:
        if "youtu.be" in video_url:
            video_id = parsed_url.path.lstrip('/')
        elif 'embed' in parsed_url.path or 'v' in parsed_url.path or 'shorts' in parsed_url.path:
            video_id = parsed_url.path.split("/")[-1]
    
    return video_id

def get_youtube_video_info(text_with_url):
    """
    Retrieves the title (if available) and transcript of a YouTube video from a string containing a URL.

    Args:
        text_with_url: The string containing the YouTube video URL.

    Returns:
        A string containing the transcript, or an error message.
    """
    try:
        video_id = extract_video_id(text_with_url)
        
        if not video_id:
            return "No YouTube URL found in the provided text."
            
        # Try to get the available transcripts
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        except Exception as e:
            # If we can't list transcripts, try to get English directly
            try:
                transcript = YouTubeTranscriptApi.get_transcript(video_id)
                formatter = TextFormatter()
                formatted_transcript = formatter.format_transcript(transcript)
                return f"Video Content:\n{formatted_transcript}"
            except Exception as inner_e:
                return f"Could not retrieve transcript: {str(inner_e)}"
        
        # Try English first, then try any available language
        try:
            transcript = transcript_list.find_transcript(['en'])
        except:
            try:
                # Get the first available transcript
                transcript = next(iter(transcript_list))
            except:
                return "No transcripts available for this video."
        
        # Fetch the transcript data
        transcript_data = transcript.fetch()
        
        # Format the transcript data
        formatter = TextFormatter()
        formatted_transcript = formatter.format_transcript(transcript_data)
        
        # Since we can't easily get the title with this API, just return the transcript
        return f"Video Content:\n{formatted_transcript}"
        
    except Exception as e:
        return f"An error occurred: {str(e)}"
