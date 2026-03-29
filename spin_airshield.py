"""
AirShield AI — The Elite Dashboard & Control Center 🛡️🎛️
Use this to manually trigger system components and verify the evolution!
"""

import os
import asyncio
import subprocess
import sys

# Attempt dynamic load of Rich for Elite UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    has_rich = True
except ImportError:
    has_rich = False

def console_print(text, style=None):
    if has_rich:
        from rich.console import Console
        Console().print(text)
    else:
        print(text)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

async def run_data_pipeline():
    console_print("[bold yellow]📡 Launching the ETL Pipeline...[/bold yellow]")
    from src.data.pipeline import run_pipeline_async
    try:
        result = await run_pipeline_async()
        
        if has_rich:
            from rich.table import Table
            from rich.console import Console
            table = Table(title="Data Ingestion Results")
            table.add_column("Source Success", style="green")
            table.add_column("Raw Readings", style="cyan")
            table.add_column("Saved to DB", style="bold green")
            table.add_row(
                f"{result.sources_succeeded}/{result.sources_attempted}",
                str(result.raw_readings),
                f"{result.saved_readings}"
            )
            Console().print(table)
        else:
            print(f"✅ Pipeline complete: {result.saved_readings} records saved.")
    except Exception as e:
        console_print(f"[bold red]❌ Pipeline Crashed: {str(e)}[/bold red]")
    
    input("\nPress Enter to return to Dashboard...")

async def run_proactive_guardian():
    console_print("[bold cyan]🛡️ Activating the Proactive Guardian...[/bold cyan]")
    from src.bot.proactive_alerts import run_proactive_guardian as guardian_fn
    try:
        await guardian_fn()
        console_print("\n[bold green]✅ Guardian scan complete. Check Telegram if any alerts were due![/bold green]")
    except Exception as e:
        console_print(f"[bold red]❌ Guardian Error: {str(e)}[/bold red]")
    input("\nPress Enter to return to Dashboard...")

async def run_self_evolution():
    console_print("[bold green]🧬 Initiating Self-Evolution Loop...[/bold green]")
    
    if has_rich:
        from rich.progress import Progress, SpinnerColumn, TextColumn
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(description="🧠 Analyzing Trends & Retraining ML Brain...", total=None)
            from src.ml.train_continuous import train_and_track
            success = await asyncio.to_thread(train_and_track)
    else:
        from src.ml.train_continuous import train_and_track
        success = await asyncio.to_thread(train_and_track)
        
    if success:
        console_print("\n[bold green]🏆 SUCCESS: AirShield has Evolved! Champion model promoted.[/bold green]")
    else:
        console_print("\n[bold yellow]⚠️ Evolution Delayed: Either lack of new data or accuracy standards not met.[/bold yellow]")
        
    input("\nPress Enter to return to Dashboard...")

def launch_bot_service():
    console_print("[bold magenta]🤖 Launching AirShield Bot & FastAPI Backend...[/bold magenta]")
    console_print("Press Ctrl+C to stop the bot and return to this dashboard.")
    try:
        # Use module-based run for clean imports
        subprocess.run([sys.executable, "-m", "src.bot.bot"])
    except KeyboardInterrupt:
        print("\nBot service stopped.")

async def main_menu():
    global has_rich
    while True:
        clear_screen()
        if has_rich:
            from rich.panel import Panel
            from rich.console import Console
            Console().print(Panel.fit(
                "[bold cyan]AirShield AI: Elite Multi-Agent Control Center[/bold cyan]\n"
                "Status: [bold green]Resilient & Ready[/bold green]",
                border_style="cyan"
            ))
        else:
            print("=== AirShield AI: Control Center ===")
            print("Status: Ready to Spin\n")
        
        console_print("1. [bold yellow]📡 Trigger ETL Pipeline[/bold yellow]")
        console_print("2. [bold cyan]🛡️ Trigger Proactive Alerts[/bold cyan]")
        console_print("3. [bold magenta]🤖 Launch Bot & Backend[/bold magenta]")
        console_print("4. [bold green]🧬 Trigger Self-Evolution (ML)[/bold green]")
        console_print("5. [bold red]❌ Exit[/bold red]")
        
        choice = input("\nSelect command (1-5): ")
        
        if choice == "1":
            await run_data_pipeline()
        elif choice == "2":
            await run_proactive_guardian()
        elif choice == "3":
            launch_bot_service()
        elif choice == "4":
            await run_self_evolution()
        elif choice == "5":
            print("Deactivating AirShield... Stay safe, buddy! 🛡️")
            break
        else:
            print("Invalid choice. Try again!")
            await asyncio.sleep(1)

if __name__ == "__main__":
    if not has_rich:
        print("Installing 'rich' for the Elite UI experience...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "rich"])
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table
            has_rich = True
        except:
            print("Installation failed, continuing in basic text mode.")
        
    try:
        asyncio.run(main_menu())
    except KeyboardInterrupt:
        print("\nForce Quit. Goodbye! 🛡️")
