# Copyright 2025 Agampreet Singh
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import argparse
import requests
import os
import signal
import sys
import glob
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from urllib.parse import urljoin

console = Console()

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def animate_typing_banner():
    clear()
    message = "Welcome Mr. Agampreet"
    colors = ["red", "gold1"]
    styled_text = Text()
    for i, char in enumerate(message):
        color = colors[i % 2]
        styled_text.append(char, style=f"bold {color}")
        console.print(styled_text, end="\r", soft_wrap=True)
        time.sleep(0.02)
    console.print()
    time.sleep(0.2)

found_paths = []

def signal_handler(sig, frame):
    console.print("\n[yellow]⛔ Scan interrupted by user. Exiting...[/yellow]")
    if found_paths:
        console.print("\n[bold green]✔ Directories found before exit:[/bold green]")
        for path in found_paths:
            console.print(f"[green]{path}[/green]")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def load_wordlist(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            words = []
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if '#' in line:
                    line = line.split('#', 1)[0].strip()
                if line:
                    words.append(line)
            return words
    except FileNotFoundError:
        console.print(f"[red]❌ Wordlist not found: {path}[/red]")
        sys.exit(1)

def scan_directories(base_url, wordlist, extensions, codes):
    global found_paths
    found = []
    total = len(wordlist) * len(extensions)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True
    ) as progress:
        task = progress.add_task("[cyan]Scanning...[/cyan]", total=total)
        for word in wordlist:
            for ext in extensions:
                path = urljoin(base_url, f"{word}{ext}")
                try:
                    r = requests.get(path, timeout=5)
                    if r.status_code in codes:
                        msg = f"[+] Found: {path} (Status: {r.status_code})"
                        console.print(f"[green]{msg}[/green]")
                        found.append(path)
                        found_paths.append(path)
                except requests.RequestException:
                    pass
                progress.update(task, advance=1)
    return found

def find_wordlists(directories=["/usr/share/wordlists", "/opt", "/usr/share/dirb", "/usr/share/seclists"]):
    found = []
    for dir in directories:
        for ext in ("*.txt", "*.lst"):
            found.extend(glob.glob(f"{dir}/**/{ext}", recursive=True))
    return sorted(set(found))

def choose_wordlist():
    console.print("[bold cyan]📂 Scanning for available wordlists...[/bold cyan]")
    wordlists = find_wordlists()

    if not wordlists:
        console.print("[red]❌ No wordlists found automatically.[/red]")
        sys.exit(1)
    else:
        for idx, path in enumerate(wordlists, 1):
            console.print(f"[{idx}] {path}")

    console.print("\n[bold yellow]Select a wordlist:[/bold yellow]")
    console.print("[green]→ Enter number to select from list[/green]")
    console.print("[green]→ Enter 'm' to input a custom path manually[/green]")

    choice = console.input("[bold magenta]> Your choice: [/bold magenta] ").strip()

    if choice.lower() == 'm':
        custom_path = console.input("[bold cyan]Enter full path to your custom wordlist: [/bold cyan]").strip()
        if os.path.isfile(custom_path):
            return custom_path
        else:
            console.print("[red]❌ Invalid file path.[/red]")
            sys.exit(1)
    elif choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(wordlists):
            return wordlists[idx]
        else:
            console.print("[red]❌ Invalid number selection.[/red]")
            sys.exit(1)
    else:
        console.print("[red]❌ Invalid input.[/red]")
        sys.exit(1)

def main():
    animate_typing_banner()

    parser = argparse.ArgumentParser(description="🔍 RedRoot Directory Brute Forcing Tool")
    parser.add_argument("-u", "--url", required=True, help="Target URL (e.g., http://example.com/)")
    parser.add_argument("-w", "--wordlist", help="Path to wordlist file (optional, will auto-scan if not provided)")
    parser.add_argument("-e", "--extensions", nargs="*", default=["/", ".php", ".html", ".bak", ".txt"], help="List of extensions to try")
    parser.add_argument("-c", "--codes", nargs="*", type=int, default=[200, 301, 302, 403], help="Valid status codes to report")

    args = parser.parse_args()

    wordlist_path = args.wordlist if args.wordlist else choose_wordlist()
    words = load_wordlist(wordlist_path)
    exts = args.extensions
    codes = args.codes

    console.print(f"[bold cyan]🌐 Target:[/bold cyan] {args.url}")
    console.print(f"[bold cyan]📖 Wordlist:[/bold cyan] {wordlist_path}")
    console.print(f"[bold cyan]🧩 Extensions:[/bold cyan] {', '.join(exts)}")
    console.print(f"[bold cyan]✅ Status Codes:[/bold cyan] {', '.join(map(str, codes))}\n")

    results = scan_directories(args.url, words, exts, codes)

    if results:
        console.print(f"\n[bold green]✔ Scan complete. Found {len(results)} valid paths.[/bold green]")
    else:
        console.print("\n[bold red]❌ No valid directories found.[/bold red]")

if __name__ == "__main__":
    main()
