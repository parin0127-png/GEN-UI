from dotenv import load_dotenv
from openai import OpenAI
import requests
import webbrowser
import os
from rich.panel import Panel
from rich.prompt import Prompt
from setting import get_api_key
from rich.console import Console
from bs4 import BeautifulSoup
from ddgs import DDGS

load_dotenv()
console = Console()
api_key = get_api_key()

client = OpenAI(
        api_key = api_key,
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
    
    keyword = prompt.replace(" ", ",") if prompt.strip() else "ui"
    
    system = """You are an expert senior UI/UX developer and visual designer with 15 years of experience building production-grade websites.

                STRICT RULES:
                - Return ONLY a complete HTML file from <!DOCTYPE html> to </html>
                - No explanation, no markdown, no code blocks, no comments outside HTML
                - All CSS inside <style> tag, all JS inside <script> tag

                IMAGE RULES — ZERO TOLERANCE FOR BROKEN IMAGES:
                - EVERY single img tag MUST follow this exact pattern:
                <img src="PRIMARY_URL" onerror="this.onerror=null;this.src='FALLBACK_URL'" alt="description">
                - NEVER use a Unsplash photo ID you are not 100% sure exists
                - ALWAYS use these guaranteed working Unsplash photos:

                GUARANTEED HOTEL/ROOM IMAGES:
                https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=800
                https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800
                https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800
                https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800
                https://images.unsplash.com/photo-1445019980597-93fa8acb246c?w=800
                https://images.unsplash.com/photo-1484154218962-a197022b5858?w=800

                GUARANTEED PEOPLE/AVATAR IMAGES:
                https://randomuser.me/api/portraits/men/1.jpg (change 1 to any number 1-99)
                https://randomuser.me/api/portraits/women/1.jpg (change 1 to any number 1-99)

                GUARANTEED CAR IMAGES:
                https://images.unsplash.com/photo-1544636331-e26879cd4d9b?w=800
                https://images.unsplash.com/photo-1555215695-3004980ad54e?w=800
                https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=800

                GUARANTEED FOOD IMAGES:
                https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=800
                https://images.unsplash.com/photo-1567620905732-2d1ec7ab7445?w=800

                GUARANTEED NATURE/TRAVEL IMAGES:
                https://images.unsplash.com/photo-1476514525535-07fb3b4ae5f1?w=800
                https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800

                UNIVERSAL FALLBACK (use in every onerror):
                https://images.unsplash.com/photo-1557804506-669a67965ba0?w=800

                RULE: If you are even 1% unsure about an image URL — use one from the guaranteed list above instead. NO EXCEPTIONS.

                DESIGN REQUIREMENTS:
                - Use Google Fonts (import via @import url)
                - Use modern CSS: flexbox, grid, animations, transitions, gradients
                - Every button must have hover effects (scale, glow, color change)
                - Every card must have hover effects (lift, shadow, border glow)
                - Navbar must be sticky with blur backdrop-filter effect
                - All sections must have smooth scroll animations using Intersection Observer
                - Use CSS variables for consistent color theming
                - Fully responsive: mobile, tablet, desktop breakpoints

                CONTENT REQUIREMENTS:
                - Use real brand names, real prices, real specifications
                - Use real people names in testimonials
                - Write real detailed descriptions not lorem ipsum
                - Every section must be fully filled with real content

                QUALITY STANDARD:
                - Output must look like built by a professional agency
                - Design must match quality of Apple Tesla Ritz Carlton official websites
                - ZERO broken images — this is non negotiable
"""

    user_message = f""" 
    Create this UI: {prompt}
    For images use Unsplash URLs like:
    https://source.unsplash.com/800x500/?{keyword}


    IMPORTANT: 
    - Use real song names, artist names, album names (not placeholders)
    - Use real emoji icons instead of image placeholders
    - Make it fully detailed and complete

    Reference data: {search_data[:300]}
    """
    console.print(f"\n[bold blue]⚡ Generating UI with {model}...[/bold blue]")
    
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
def main():
    while True:
        current_model_index[0] = 0

        console.print(Panel.fit(
            f"[bold cyan]Active model:[/bold cyan] [green]{get_current_model()}[/green]\n",
            border_style="cyan"
        ))

        prompt = Prompt.ask("[bold yellow]✨ You[/bold yellow]")

        if prompt.lower() == 'exit':
            console.print(Panel("[bold cyan]👋 Bye! Thanks for using GEN-UI![/bold cyan]", border_style="cyan"))
            break
        

        search_result = web_search(prompt + " UI design HTML CSS JS")
        skip_scrape = any(w in prompt.lower() for w in ['website' , 'landing', 'dealership', 'portfolio' , 'clone'])
        url = get_first_url(search_result)
        scraped_data = "Be creative , no reference needed." if skip_scrape else (scrape_page(url) if url else "No URL found ")
        html = generate_html(prompt, search_result, scraped_data)

        if html:
            save_open(html)
        else : 
            console.print("[bold red]❌ Failed to generate UI[/bold red]")
        
        console.rule("[dim cyan]─[/dim cyan]")

if __name__ == "__main__":
    main()