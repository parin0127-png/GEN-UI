from dotenv import load_dotenv
from openai import OpenAI
import requests
import webbrowser
import os
import json
import time
from rich.console import Console
from bs4 import BeautifulSoup
from ddgs import DDGS

load_dotenv()
console = Console()

client = OpenAI(
    api_key=os.getenv("CEREBRAS_API_KEY"),
    base_url="https://api.cerebras.ai/v1"
)
MODELS = [
    "qwen-3-235b-a22b-instruct-2507",  
    "gpt-oss-120b",                     
    "zai-glm-4.7",                      
    "llama3.1-8b",
]
last_token_used = [0]
current_model_index = [0]

def get_first_url(search_result: str):
    for line in search_result.split("\n"):
        if "Url :" in line:
            return line.replace("Url :", "").strip()
    return ""

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
    
def generate_html(prompt : str, search_data: str, scrape_data : str):
    model = get_current_model()

    if not model :
        print("> Models are not available !")
        return None
    
    system = """You are an expert senior UI/UX developer and visual designer with 15 years of experience building production-grade websites.

STRICT RULES:
- Return ONLY a complete HTML file from <!DOCTYPE html> to </html>
- No explanation, no markdown, no code blocks, no comments outside HTML
- All CSS inside <style> tag, all JS inside <script> tag

DESIGN REQUIREMENTS:
- Use Google Fonts (import via @import url)
- Use modern CSS: flexbox, grid, animations, transitions, gradients
- Every button must have hover effects (scale, glow, color change)
- Every card must have hover effects (lift, shadow, border glow)
- Navbar must be sticky with blur backdrop-filter effect
- All sections must have smooth scroll animations
- Use CSS variables for consistent color theming
- Add subtle particle or gradient animations in hero section
- All images must be real Unsplash URLs — never leave image slots empty
- Every section must be fully filled with real content, no placeholders
- Fully responsive: mobile, tablet, desktop breakpoints

CONTENT REQUIREMENTS:
- Use real brand names, real prices, real specifications
- Use real people names in testimonials
- Write real, detailed descriptions (not lorem ipsum)
- Every section must tell a story and feel premium

QUALITY STANDARD:
- Output must look like it was built by a professional agency
- Design must match quality of Apple, Tesla, Lamborghini official websites
- Every pixel must have purpose and intention"""

    user_message = f""" 
    Create this UI: {prompt}
    For images use Unsplash URLs like:
    https://source.unsplash.com/800x500/?{prompt.split()[0]}


    IMPORTANT: 
    - Use real song names, artist names, album names (not placeholders)
    - Use real emoji icons instead of image placeholders
    - Make it fully detailed and complete

    Reference data: {search_data[:300]}
    """
    console.print(f"[blue]> Generating UI with {model}...[/blue]")
    
    while current_model_index[0] < len(MODELS):
        model = get_current_model()
        try : 
            response = client.chat.completions.create(
                model = model,
                messages = [
                    {"role" : "system" , "content" : system},
                    {"role" : "user" , "content" : user_message}
                ],
                max_tokens = 16000,
            )
            used = response.usage.total_tokens
            print(f"> [{model}] Tokens used: {used}")
            return response.choices[0].message.content
        except Exception as e:
            console.print(f"[yellow]> Switching from {model} due to: {e}[/yellow]")
            current_model_index[0] += 1
    
    return None

def save_open(html : str):
    if "<!DOCTYPE html>" in html:
        start = html.find("<!DOCTYPE html>")
        end = html.rfind("</html>")

        if start != -1 and end != -1:
            html = html[start : end + 7]
            os.makedirs("outputs" , exist_ok = True)
            with open("outputs/output.html" , "w" , encoding = "utf-8") as f:
                f.write(html)

            path = os.path.abspath("outputs/output.html").replace("\\", "/")
            webbrowser.open(f"file:///{path}")
            print("> Saved and opened !")
            return
    print("> Warning : Could not extract valid HTML.")

while True:
    current_model_index[0] = 0

    print(f"\n> Active model: {get_current_model()}")
    print("> Enter a prompt to make an absolute UI!")
    prompt = input("> You : ")

    if prompt.lower() == 'exit':
        print("> Bye !")
        break
    

    search_result = web_search(prompt + " UI design HTML CSS JS")
    skip_scrape = any(w in prompt.lower() for w in ['website' , 'landing', 'dealership', 'portfolio' , 'clone'])
    url = get_first_url(search_result)
    scraped_data = "Be creative , no reference needed." if skip_scrape else (scrape_page(url) if url else "No URL found ")
    html = generate_html(prompt, search_result, scraped_data)

    if html:
        save_open(html)
    else : 
        print("> Failed to generate UI ")