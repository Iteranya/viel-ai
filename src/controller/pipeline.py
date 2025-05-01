import re
import config
from src.discordo import Discordo
from src.aicharacter import AICharacter
from src.dimension import Dimension
from src.prompts import PromptEngineer
from src.llm import LlmApi
from src.models  import QueueItem
from src.multimodal import MultiModal
from src.duckduckgo import Bebek
import src.textutil as textutil
from src.docreader import DocReader
from src import youtube
import traceback
inline_comprehension = True
async def think() -> None:

    while True:
        content = await config.queue_to_process_everything.get()
        discordo:Discordo = content["discordo"]
        bot:AICharacter = content["bot"]
        video_content = ""
        await discordo.initialize_channel_history()
        dimension:Dimension = content["dimension"]
        file = None
        try:
            await discordo.raw_message.add_reaction('✨')
        except Exception as e:
            print("Hi!")
        if discordo.raw_message.attachments:
            if discordo.raw_message.attachments[0].filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
                images = await discordo.process_attachment()
            else:
                file = await discordo.save_attachment()
        message_content = discordo.get_user_message_content()
        safesearch='on'
        if youtube.contains_youtube_link(message_content):
            print("Retrieving Video Data...")
            video_content = youtube.get_youtube_video_info(message_content)
            discordo.video_caption = f"[System Note: User Sent The Following Video: {video_content}]"

        # if message_content.startswith(">"):
        #     await send_lam_message(bot,discordo,dimension)
        if message_content.startswith("//"):
            pass
        elif message_content.startswith("^"):
            top_result = ""
            image_result = None
            bebek = Bebek(message_content)
            if "news" in message_content:
                top_result = await bebek.get_news()                
            else:
                top_result = await bebek.get_top_search_result()
            if "image" in message_content or "picture" in message_content:
                    if discordo.get_channel().is_nsfw == True:
                        safesearch='off'
                    image_result = await bebek.get_image_link(safesearch)
            elif "video" in message_content:
                    video_result = await bebek.get_video_link()
                    video_result = "[System Note: Attachment]\n"+video_result

            await send_grounded_message(bot,discordo,dimension,str(top_result),image_result,video_result)
        elif discordo.raw_message.attachments:
                multimodal = MultiModal(discordo)
                await send_multimodal_message(bot,discordo,dimension,multimodal,file)
        else:
            await send_llm_message(bot,discordo,dimension)
        config.queue_to_process_everything.task_done()


async def send_multimodal_message(bot: AICharacter,discordo: Discordo,dimension:Dimension, multimodal: MultiModal, file):
        print("Multimodal Processing...")
        additional = ""
        if file!=None:
            keyword = re.search(r"\((.*?)\)", discordo.get_user_message_content())
            reader = DocReader(file,keyword)
            additional = await reader.llm_eval()
        else:
            additional = await multimodal.read_image()
        if config.immersive_mode:
            discordo.history+="\n[System Note: User sent the following attachment:"+str(additional)+"]"
        else:
            discordo.send_as_user("[System Note: User sent the following attachment:"+str(additional)+"]")
        prompter = PromptEngineer(bot,discordo,dimension)
        queueItem = QueueItem(prompt=await prompter.create_text_prompt())
        llmapi = LlmApi(queueItem,prompter)
        queueItem = await llmapi.send_to_model_queue()
        await discordo.send(bot,queueItem)
        return

async def send_grounded_message(bot: AICharacter,discordo: Discordo,dimension:Dimension,top_message:str,images=None,videos=""):
    print("Grounding Processing...")
    if top_message!="" and top_message!=None:
        discordo.history+="\n[System Note: Web Search result: "+top_message+"]"

    print("Chat Completion Processing...")
    prompter = PromptEngineer(bot,discordo,dimension)
    queueItem = QueueItem(prompt=await prompter.create_text_prompt())
    llmapi = LlmApi(queueItem,prompter)
    queueItem = await llmapi.send_to_model_queue()
    if images!="" and images!=None:
        textutil.clean_links(queueItem.result)
        queueItem.images = images
    if videos!="" and videos!=None:
         queueItem.result+="\n"+videos
    await discordo.send(bot,queueItem)
    return

async def send_llm_message(bot: AICharacter,discordo: Discordo,dimension:Dimension):
    prompter = PromptEngineer(bot,discordo,dimension)
    queueItem = QueueItem(prompt=await prompter.create_text_prompt())
    llmapi = LlmApi(queueItem,prompter)
    print("Chat Completion Processing...")
    queueItem = await llmapi.send_to_model_queue()
    await discordo.send(bot,queueItem)
    return
