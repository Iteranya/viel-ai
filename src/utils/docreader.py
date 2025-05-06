import PyPDF2
import aiohttp
import google.generativeai as genai


class DocReader:
    def __init__(self, path, keyword=None):
        self.path = path
        self.text = self.pdf_to_text(path)
        self.keyword= keyword
    
    def pdf_to_text(self, file_path):
        try:
            # Check the file extension
            if file_path.lower().endswith('.pdf'):
                with open(file_path, 'rb') as pdf_file:
                    pdf_reader = PyPDF2.PdfReader(pdf_file)
                    num_pages = len(pdf_reader.pages)
                    text = ""
                    for page_num in range(num_pages):
                        page = pdf_reader.pages[page_num]
                        text += page.extract_text()
                return text
            
            elif file_path.lower().endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as txt_file:
                    text = txt_file.read()
                return text
            
            else:
                print(f"Error: Unsupported file type. Please provide a PDF or TXT file.")
                return None

        except FileNotFoundError:
            print(f"Error: File not found at {file_path}")
            return None
        except PyPDF2.errors.PdfReadError:
            print(f"Error: Could not read PDF. The file might be corrupted or encrypted.")
            return None
        except UnicodeDecodeError:
            # Try reading with a different encoding if UTF-8 fails
            try:
                with open(file_path, 'r', encoding='latin-1') as txt_file:
                    text = txt_file.read()
                return text
            except Exception as e:
                print(f"Error reading text file: {e}")
                return None
        except Exception as e:  # Catch other potential errors
            print(f"An unexpected error occurred: {e}")
            return None
    
    async def llm_eval(self):
        if not self.text:
            print("No text to evaluate")
            return None
        gemini_eval = await self.gemini_eval()
        if gemini_eval==None:
            return await self.router_eval()
        else:
            return gemini_eval

    async def gemini_eval(self):
        genai.configure(api_key=config.gemini_token)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        prompt = f"[{self.text}] \n=====\n Write a summary followed with a detailed analysis of the text above in Markdown Format. If it's a work of fiction/story, highlight the overall story, plot, narrative, worldbuilding, and characters. If it's a formal document, highlight the background, the methodology if any, the details, and results if any."
        if self.keyword!=None:
            prompt = f"[{self.text}] \n=====\n Write a summary of the text above in Markdown Format. If it's a work of fiction/story, highlight the overall story, plot, narrative, worldbuilding, and characters. If it's a formal document, highlight the background, the methodology if any, the details, and results if any."
            prompt = f"{prompt}\n[Additional Note: {self.keyword}]"
        response = await model.generate_content_async(prompt)

        return response.text

    async def router_eval(self, 
                       include_image_url=None):

        
        model = config.text_evaluator_model
        final_prompt = f"[{self.text}] \n=====\n Write a summary followed with a detailed analysis of the text above in Markdown Format. If it's a work of fiction/story, highlight the overall story, plot, narrative, worldbuilding, and characters. If it's a formal document, highlight the background, the methodology if any, the details, and results if any."
        if self.keyword!=None:
            final_prompt = f"{final_prompt}\n[Additional Note: The Keyword/Theme/Concept/Character To Keep Track Of As Focal point: {self.keyword}]"
        # Prepare messages payload
        messages = [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": final_prompt
                }
            ]
        }]
        
        # Add image if provided
        if include_image_url:
            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": include_image_url
                }
            })
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {config.openrouter_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": model,
                        "messages": messages
                    }
                ) as response:
                    # Raise exception for bad HTTP status
                    response.raise_for_status()
                    result = await response.json()
                    print(str(result))
                    if result.get('choices',None)!=None:
                        return result['choices'][0]['message']['content']
                    else:
                        return f"Error Reading File: {result['error']['message']}, Notify User That An Error Occured."
        except aiohttp.ClientError as e:
            print(f"Network error in LLM evaluation: {e}")
        except (KeyError, ValueError) as e:
            print(f"Parsing error in LLM response: {e}")
        except Exception as e:
            print(f"Unexpected error in LLM evaluation: {e}")
        
        return None
