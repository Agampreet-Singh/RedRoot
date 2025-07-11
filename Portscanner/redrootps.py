#!/usr/bin/env python3
import argparse
import subprocess
import time
import os
from datetime import datetime
from xml.etree import ElementTree as ET
from rich.console import Console
from rich.table import Table
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
        time.sleep(0.02)
    console.print()  # newline
    time.sleep(0.2)

def run_nmap_scan_xml(target, ports, arguments):
    cmd = ["nmap", "-p", ports, "-oX", "-", *arguments.split(), target]
    console.print(f"[+] Running scan on {target} (ports: {ports})\n", style="bold cyan")
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError:
        console.print("[-] Scan could not be completed due to an internal error. Please check the target and try again.", style="bold red")
        return None
    except Exception:
        console.print("[-] An unexpected error occurred during the scan process.", style="bold red")
        return None

def parse_nmap_xml(xml_data):
    try:
        root = ET.fromstring(xml_data)
    except ET.ParseError:
        console.print("[-] Failed to parse scan output. Output may be malformed.", style="bold red")
        return None

    report = {}
    host_elem = root.find("host")
    if host_elem is None:
        return None

    addr = host_elem.find("address[@addrtype='ipv4']")
    hostname_elem = host_elem.find("hostnames/hostname")
    ip = addr.get("addr") if addr is not None else "Unknown"
    hostname = hostname_elem.get("name") if hostname_elem is not None else "N/A"

    report['ip'] = ip
    report['hostname'] = hostname

    os_elem = host_elem.find("os/osmatch")
    if os_elem is not None:
        report['os'] = os_elem.get("name")
        report['os_accuracy'] = os_elem.get("accuracy")
    else:
        report['os'] = "Unknown"
        report['os_accuracy'] = "0"

    ports = []
    for port in host_elem.findall("ports/port"):
        portid = port.get("portid")
        protocol = port.get("protocol")
        state_elem = port.find("state")
        service_elem = port.find("service")

        state = state_elem.get("state") if state_elem is not None else "unknown"
        service_name = service_elem.get("name") if service_elem is not None else "unknown"
        service_version = service_elem.get("version", "") if service_elem is not None else ""

        scripts = []
        for script in port.findall("script"):
            sid = script.get("id")
            output = script.get("output")
            if sid and output:
                scripts.append({"id": sid, "output": output})

        ports.append({
            "port": portid,
            "protocol": protocol,
            "state": state,
            "service": service_name,
            "version": service_version,
            "scripts": scripts
        })
    report['ports'] = ports

    return report

def display_scan_report(report):
    clear()
    console.rule("[bold red]RedRoot - Portscanner Report[/bold red]")
    console.print(f"[bold yellow]Target IP:[/bold yellow] {report['ip']}")
    console.print(f"[bold yellow]Hostname:[/bold yellow] {report['hostname']}")
    console.print(f"[bold yellow]Detected OS:[/bold yellow] {report['os']} (Accuracy: {report['os_accuracy']}%)\n")

    table = Table(title="Open Ports", header_style="bold magenta")
    table.add_column("Port", justify="center")
    table.add_column("Protocol", justify="center")
    table.add_column("State", justify="center")
    table.add_column("Service", justify="center")
    table.add_column("Version", justify="left")

    open_ports = [p for p in report['ports'] if p['state'] == 'open']

    if not open_ports:
        console.print("[bold red]No open ports found.[/bold red]")
        return

    for p in open_ports:
        version = p['version'] if p['version'] else "-"
        table.add_row(p['port'], p['protocol'], p['state'], p['service'], version)
    console.print(table)

    for p in open_ports:
        if p['scripts']:
            console.print(f"\n[bold cyan]Scripts output for port {p['port']}/{p['protocol']} ({p['service']}):[/bold cyan]")
            for script in p['scripts']:
                console.print(f"[bold green]{script['id']}:[/bold green]")
                for line in script['output'].splitlines():
                    console.print(f"  {line}")
    console.rule("[bold green]Scan Complete[/bold green]")

def save_output(report, filename):
    try:
        with open(filename, "w") as f:
            f.write(f"RedRoot Portscanner Report\n")
            f.write(f"Target IP: {report['ip']}\n")
            f.write(f"Hostname: {report['hostname']}\n")
            f.write(f"Detected OS: {report['os']} (Accuracy: {report['os_accuracy']}%)\n\n")
            f.write("Open Ports:\n")
            for p in report['ports']:
                if p['state'] == 'open':
                    version = p['version'] if p['version'] else "-"
                    f.write(f" - {p['port']}/{p['protocol']} {p['service']} Version: {version}\n")
                    if p['scripts']:
                        f.write(f"   Scripts output:\n")
                        for script in p['scripts']:
                            f.write(f"    [{script['id']}]:\n")
                            for line in script['output'].splitlines():
                                f.write(f"      {line}\n")
        console.print(f"[+] Output saved to {filename}", style="bold green")
    except Exception:
        console.print(f"[-] Could not save the output file. Please check permissions or path.", style="bold red")

def main():
    animate_typing_banner()

    parser = argparse.ArgumentParser(
        description="RedRoot - Advanced Port Scanner",
        epilog="Example:\n  redrootps 192.168.1.1 -p 22-443 -A -O --save scan.txt",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("target", help="Target IP, hostname or CIDR")
    parser.add_argument("-p", "--ports", default="1-1000", help="Port range (default: 1-1000)")
    parser.add_argument("-A", "--aggressive", action="store_true", help="Enable aggressive scan")
    parser.add_argument("-O", "--osdetect", action="store_true", help="Enable OS detection")
    parser.add_argument("-s", "--scripts", help="Run specific NSE scripts (comma separated)")
    parser.add_argument("-T", "--timing", default="4", help="Timing template (0-5, default: 4)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase output verbosity")
    parser.add_argument("--save", help="Save output to file")

    args = parser.parse_args()
    start = datetime.now()

    scan_args = f"-sS -T{args.timing}"
    if args.aggressive:
        scan_args += " -A"
    if args.osdetect:
        scan_args += " -O"
    if args.verbose:
        scan_args += " -v"
    if args.scripts:
        scan_args += f" --script={args.scripts}"

    xml_output = run_nmap_scan_xml(args.target, args.ports, scan_args)
    if not xml_output:
        console.print("[-] No scan data to display.", style="bold red")
        return

    report = parse_nmap_xml(xml_output)
    if not report:
        console.print("[-] Failed to parse scan results.", style="bold red")
        return

    display_scan_report(report)

    if args.save:
        save_output(report, args.save)

    duration = datetime.now() - start
    console.print(f"[+] Scan completed in {duration}", style="bold yellow")

if __name__ == "__main__":
    main()
