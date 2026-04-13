from dotenv import load_dotenv
from groq import Groq
import requests
import webbrowser
import os
import json
from bs4 import BeautifulSoup
from ddgs import DDGS

load_dotenv()

client = Groq(api_key = os.getenv("GROQ_API_KEY"))

MODELS = [  
    "llama-3.3-70b-versatile", 
    "moonshotai/kimi-k2-instruct",   
    "openai/gpt-oss-20b",            
    "openai/gpt-oss-120b",    
    "llama-3.1-8b-instant",
    "qwen/qwen3-32b"             
]

last_token_used = [0]
current_model_index = [0]

def get_current_model():
    if current_model_index[0] < len(MODELS):
        return MODELS[current_model_index[0]]
    return "No models available"

def web_search(query: str):
    """Search web for UI examples and return results."""
    results = []
    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results = 3):
            results.append(f"Title {r['title']} \n Url : {r['href']} \n Snippet : {r['body']}")
    return "\n".join(results)

def scrape_page(url : str):
    try :
        res = requests.get(url, timeout = 5)
        soup = BeautifulSoup(res.text, "html.parser")
        styles = [s.get_text() for s in soup.find_all("style")]
        text = soup.get_text(separator = "\n" , strip = True)[:500]
        css_text = "\n".join(styles)[:200]
        
        return f"Page Text : \n{text} \n CSS found : \n{css_text}"
    except Exception as e:
        return f"Couldn't scrape : {e}"
tools = [
     {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the web for UI design examples, CSS patterns, HTML templates and inspiration",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "search query like 'glassmorphism login form CSS'"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scrape_page",
            "description": "Visit a URL and scrape its HTML and CSS code to use as reference",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "the URL to scrape"
                    }
                },
                "required": ["url"]
            }
        }
    }
]

def run_tools(name , args):
    if name == "web_search":
        return web_search(**args)
    elif name == "scrape_page":
        return scrape_page(**args)
    else:
        return "> Unknown command !"
    
retry_count = [0]
def call_api(messages):
    while current_model_index[0] < len(MODELS):
        model = get_current_model()
        try:
            response = client.chat.completions.create(
                model = model,
                messages = messages,
                tools = tools,
                tool_choice = "auto",
                max_tokens = 8000
            )

            used = response.usage.total_tokens
            last_token_used[0] = used
            print(f"> [{model}] Tokens used this call : {used}")
            return response
        except Exception as e:
            error_msg = str(e).lower()

            if "400" in error_msg or "tool_use_failed" in error_msg:
                print(f"> [{model}] Tool calling broken ! Switching model....")
                current_model_index[0] += 1
                if current_model_index[0] < len(MODELS):
                    next_model = get_current_model()
                    print(f"> Switching to : {next_model}")
                else:
                    print("> All models are exhausted for today. Try again tomorrow !")
                    return None

            elif "rate_limit_exceeded" in error_msg or "429" in error_msg:
                if "per minute" in error_msg or "tpm" in error_msg:
                    retry_count[0] += 1
                    if retry_count[0] >= 3:
                        print(f"> [{model}] Too many retries ! Switching model...")
                        retry_count[0] = 0
                        current_model_index[0] += 1
                        if current_model_index[0] < len(MODELS):
                            print(f"> Switching to : {get_current_model()}")
                        else:
                            print("> all model exhusted !")
                    else : 
                        print(f"> [{model}] per-minute limit hit ! Retry {retry_count[0]} Waiting 60 seconds....")
                        import time
                        time.sleep(60)
                        print("> Retrying now......")                 
                elif "per day" in error_msg or "tpd" in error_msg:
                    print(f"> [{model}] Daily limit hit ! Switching model....")
                    current_model_index[0] += 1

                    if current_model_index[0] < len(MODELS):
                        print(f"> Switching to : {get_current_model()} !")
                    else : 
                        print("> All models are exhausted for today. Try again tomorrow !")
                        return None  

                else :
                    print(f"> [{model}] Rate limit hit ! Waiting for 30 seconds.....")
                    import time
                    time.sleep(30)
            else:
                print(f"> API Error : {e}")
                raise

    return None

    
def run_conversation(prompt , messages):
    messages.append({"role" : "user" , "content" : prompt})

    while True:
        response = call_api(messages) 

        if response is None:
            print("> Could not get a response. All models are at their limit.")
            break
        message = response.choices[0].message

        if not message.tool_calls:
            print(f"> AI : {message.content}")

            if "<!DOCTYPE html>" in message.content:
                start = message.content.find("<!DOCTYPE html")
                end = message.content.rfind("</html>")

                if start != -1 and end != -1 :
                    html = message.content[start : end + 7]
                    os.makedirs("outputs" , exist_ok = True)
                    with open("outputs/output.html", "w" , encoding = "utf-8") as f:
                        f.write(html)
                    path = os.path.abspath("outputs/output.html").replace("\\" , "/")
                    webbrowser.open(f"file:///{path}")
                    print("> Saved and Opened !")
                else : 
                    print("> Warning: Could not extract valid HTML from response.")
            break

        messages.append(message)

        chat_history = []
        for tool_call in message.tool_calls:
            try:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                result = run_tools(name, args)
                print(f"Tool {name} calling........")

                chat_history.append({
                    "role" : "tool",
                    "tool_call_id" : tool_call.id,
                    "content" : str(result)
                })
            except Exception as e : 
                print(f"Error : {e}")

                chat_history.append({
                    "role" : "tool",
                    "tool_call_id" : tool_call.id,
                    "content" : f"Error : {e}"
                })
        for r in chat_history:
            messages.append(r)


# while True:
    # print(f"> Active model : {get_current_model()}")
    # print("> Enter a prompt to make an absoluate UI !")
    # prompt = input("> You : ")

    # if prompt.lower() == "exit":
        # print("> BYE !")
        # break

    # if current_model_index[0] >= len(MODELS):
        # print("> All models are exhausted. Come back tomorrow !")
        # break
    
    # messages = [
        #   {
        # "role": "system",
        # "content": """You are an expert UI developer.
# Follow these steps in order:
# 1. Call web_search ONCE to find UI examples
# 2. Call scrape_page ONCE on the best URL from results
# 3. After getting results, return ONLY the complete HTML file in your response
# 4. HTML must start with <!DOCTYPE html> and end with </html>
# 5. All CSS inside <style> tag, all JS inside <script> tag
# 6. Do NOT call any other tools
# 7. Do NOT ask any questions
# 8. Do NOT add any explanation before or after the HTML"""
        # }
    # ]
    # run_conversation(prompt, messages)