import json
import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt


console = Console()

CONFIG_FILE = os.path.expanduser("~/.genui_config.json")

def get_api_key():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)

            if config.get("api_key"):
                return config['api_key']
            
    console.print(Panel.fit(
        "[bold cyan]🎨 Welcome to GEN-UI![/bold cyan]\n\n"
        "[white]You need a [bold yellow]FREE[/bold yellow] Cerebras API key to get started.[/white]",
        border_style="cyan"
    ))

    console.print("\n[bold white]📌 Follow these steps:[/bold white]")
    console.print("   [cyan]1.[/cyan] Go to 👉  [bold underline cyan]https://cloud.cerebras.ai[/bold underline cyan]")
    console.print("   [cyan]2.[/cyan] Create a free account")
    console.print("   [cyan]3.[/cyan] Click on [bold]'API Keys'[/bold] in the sidebar")
    console.print("   [cyan]4.[/cyan] Click [bold]'Create New Key'[/bold]")
    console.print("   [cyan]5.[/cyan] Copy and paste it below\n")

    while True:
        api_key = Prompt.ask("[bold yellow]🔑 Paste your Cerebras API key[/bold yellow]").strip()

        if not api_key:
            console.print("[red]❌ API key cannot be empty. Please try again.[/red]\n")
            continue

        if not api_key.startswith("csk-"):
            console.print("[yellow]⚠️  That doesn't look like a valid Cerebras key.[/yellow]")
            console.print("   It should start with [bold]'csk-'[/bold]")
            retry = Prompt.ask("   Try again?", choices=["y", "n"], default="y")
            if retry != 'y':
                exit(1)
                continue
        
        break

    with open(CONFIG_FILE , "w") as f:
        json.dump({"api_key" : api_key} , f)
    
    console.print("\n[bold green]✅ API key saved! You won't need to enter it again.[/bold green]")

    return api_key