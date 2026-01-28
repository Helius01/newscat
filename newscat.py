import feedparser
import sys
from datetime import datetime
from typing import List, Dict

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.prompt import Prompt
    from rich.markdown import Markdown
    from rich import box
except ImportError:
    print("Installing required dependencies...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "feedparser", "rich", "--break-system-packages"])
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.prompt import Prompt
    from rich.markdown import Markdown
    from rich import box

console = Console()

RSS_URL = "https://news.ycombinator.com/rss"

def fetch_feed(url: str) -> List[Dict]:
    
    try:
        with console.status("[bold green]Fetching latest Hacker News stories...", spinner="dots"):
            feed = feedparser.parse(url)
        
        if feed.bozo:
            console.print("[bold red]Error parsing feed!", style="bold red")
            return []
        
        return feed.entries
    except Exception as e:
        console.print(f"[bold red]Error fetching feed: {e}")
        return []

def create_header():
    header_text = Text()
    header_text.append("🔥 ", style="bold red")
    header_text.append("HACKER NEWS", style="bold orange1")
    header_text.append(" 🔥", style="bold red")
    header_text.append("\n")
    header_text.append("Your Terminal RSS Reader", style="italic cyan")
    
    return Panel(
        header_text,
        box=box.DOUBLE,
        border_style="bright_yellow",
        padding=(1, 2)
    )

def format_time(published_parsed):
    if published_parsed:
        dt = datetime(*published_parsed[:6])
        now = datetime.now()
        diff = now - dt
        
        if diff.days > 0:
            return f"{diff.days}d ago"
        elif diff.seconds >= 3600:
            return f"{diff.seconds // 3600}h ago"
        elif diff.seconds >= 60:
            return f"{diff.seconds // 60}m ago"
        else:
            return "just now"
    return "unknown"

def display_feeds(entries: List[Dict]):
    if not entries:
        console.print("[yellow]No stories found!")
        return
    
    table = Table(
        show_header=True,
        header_style="bold magenta",
        border_style="bright_blue",
        box=box.ROUNDED,
        expand=True,
        row_styles=["", "dim"]
    )
    
    table.add_column("#", style="cyan", width=4, justify="center")
    table.add_column("📰 Title", style="white", no_wrap=False)
    table.add_column("⏰ Time", style="green", width=12)
    table.add_column("👤 Author", style="yellow", width=15)
    
    for idx, entry in enumerate(entries[:30], 1):
        title = entry.get('title', 'No title')
        link = entry.get('link', '')
        author = entry.get('author', 'Unknown')
        published = format_time(entry.get('published_parsed'))
        
        clickable_title = f"[link={link}]{title}[/link]"
        
        table.add_row(
            str(idx),
            clickable_title,
            published,
            author
        )
    
    console.print(table)

def display_story_details(entry: Dict):
    title = entry.get('title', 'No title')
    link = entry.get('link', '')
    author = entry.get('author', 'Unknown')
    published = format_time(entry.get('published_parsed'))
    comments_link = entry.get('comments', '')
    
    details = f"""
## {title}

**👤 Author:** {author}
**⏰ Posted:** {published}
**🔗 Link:** [{link}]({link})
**💬 Comments:** [{comments_link}]({comments_link})
    """
    
    console.print(Panel(
        Markdown(details),
        border_style="cyan",
        box=box.DOUBLE
    ))

def interactive_mode(entries: List[Dict]):
    while True:
        console.print("\n[bold cyan]Commands:[/bold cyan]")
        console.print("  • Type a number (1-30) to view story details")
        console.print("  • Type 'r' to refresh")
        console.print("  • Type 'q' to quit")
        
        choice = Prompt.ask("\n[bold yellow]What would you like to do?[/bold yellow]", default="q")
        
        if choice.lower() == 'q':
            console.print("[bold green]Thanks for reading! 👋")
            break
        elif choice.lower() == 'r':
            console.clear()
            new_entries = fetch_feed(RSS_URL)
            if new_entries:
                entries = new_entries
            console.print(create_header())
            display_feeds(entries)
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(entries):
                console.clear()
                display_story_details(entries[idx])
            else:
                console.print("[red]Invalid story number!")
        else:
            console.print("[red]Invalid command!")

def main():
    try:
        console.clear()
        console.bell()
        console.print(create_header())
        
        entries = fetch_feed(RSS_URL)
        
        if not entries:
            console.print("[red]Failed to fetch stories. Please check your internet connection.")
            return
        
        display_feeds(entries)
        
        console.print(f"\n[bold green]✨ Showing {min(len(entries), 30)} latest stories from Hacker News")
        console.print("[dim]💡 Tip: Click on any title to open the link in your browser![/dim]\n")
        
        interactive_mode(entries)
        
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Interrupted! Goodbye! 👋")
    except Exception as e:
        console.print(f"[bold red]An error occurred: {e}")

if __name__ == "__main__":
    main()
