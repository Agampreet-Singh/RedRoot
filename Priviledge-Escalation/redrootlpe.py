#!/usr/bin/env python3
import os
import pwd
import grp
import json
import time
import platform
import subprocess
from datetime import datetime
from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

console = Console()
results = {
    "user": {},
    "os": {},
    "suid": [],
    "writable_configs": [],
    "cron_jobs": [],
    "sudo": {},
    "env": {},
    "fstab": [],
    "capabilities": [],
    "kernel_exploits": [],
    "docker": False
}

GTFOBINS = ["nmap", "vim", "less", "nano", "awk", "perl", "python", "find", "bash", "cp", "tar", "more", "tee", "lua"]


def clear():
    os.system('clear' if os.name != 'nt' else 'cls')


def animate_banner():
    clear()
    text = Text()
    message = "Welcome Mr. Agampreet"
    for i, char in enumerate(message):
        color = "red" if i % 2 == 0 else "gold1"
        text.append(char, style=f"bold {color}")
        console.print(text, end="\r")
        time.sleep(0.04)
    console.print(text)
    time.sleep(0.3)


def redroot_header():
    console.print("\n[bold red]🔧 REDROOT LINUX PRIVILEGE ESCALATION TOOL[/bold red]", justify="center")
    console.print("[cyan]Advanced Local Enumeration with GTFOBins and Exploit Mapping[/cyan]\n", justify="center")


def section(title):
    console.print(Panel(f"[bold cyan]{title}[/bold cyan]", expand=False))


def run(cmd):
    return subprocess.getoutput(cmd)


def get_user_info():
    user = pwd.getpwuid(os.getuid())[0]
    groups = [grp.getgrgid(g).gr_name for g in os.getgroups()]
    results["user"] = {"name": user, "groups": groups}
    console.print(f"[green][+][/green] User: {user} | Groups: {', '.join(groups)}")


def get_os_info():
    results["os"] = {
        "uname": run("uname -a"),
        "os_release": run("cat /etc/os-release")
    }
    console.print(f"[green][+][/green] Kernel: {results['os']['uname']}")


def find_suid_binaries():
    section("SUID Binaries (GTFOBins)")
    output = run("find / -perm -4000 -type f 2>/dev/null")
    for path in output.splitlines():
        for bin in GTFOBINS:
            if f"/{bin}" in path:
                results["suid"].append(path)
                console.print(f"[yellow][GTFO][/yellow] {path}")


def check_writable_configs():
    section("Writable Configs")
    files = run("find /etc -writable -type f 2>/dev/null")
    for file in files.splitlines():
        results["writable_configs"].append(file)
        console.print(f"[red][W][/red] Writable: {file}")


def check_cron_jobs():
    section("Cron Jobs")
    cron_dirs = ["/etc/cron.d", "/etc/cron.daily", "/etc/cron.hourly", "/etc/cron.weekly", "/var/spool/cron"]
    for dir in cron_dirs:
        if os.path.exists(dir):
            for root, dirs, files in os.walk(dir):
                for file in files:
                    path = os.path.join(root, file)
                    results["cron_jobs"].append(path)
                    console.print(f"[blue][CRON][/blue] {path}")


def sudo_privs():
    section("Sudo Permissions")
    sudo = run("sudo -l")
    results["sudo"] = sudo
    console.print(sudo)


def env_vars():
    section("Environment Variables")
    results["env"] = dict(os.environ)
    for k, v in os.environ.items():
        console.print(f"[green]{k}[/green]=[yellow]{v}[/yellow]")


def parse_fstab():
    section("Mounted Filesystems (/etc/fstab)")
    if os.path.exists("/etc/fstab"):
        with open("/etc/fstab") as f:
            lines = f.readlines()
            results["fstab"] = lines
            for l in lines:
                console.print(f"[grey58]{l.strip()}[/grey58]")


def check_capabilities():
    section("File Capabilities")
    caps = run("getcap -r / 2>/dev/null")
    for line in caps.splitlines():
        results["capabilities"].append(line)
        console.print(f"[magenta][CAP][/magenta] {line}")


def detect_docker():
    if os.path.exists("/.dockerenv") or run("grep -q docker /proc/1/cgroup && echo Yes") == "Yes":
        results["docker"] = True
        console.print("[blue][DOCKER][/blue] Running inside Docker")


def kernel_exploit_suggestions():
    section("Exploit Mapping (Kernel-Based)")
    kernel = platform.release()
    suggestions = {
        "4.4": "Dirty COW", "3.10": "Overlayfs", "5.8": "CAP_SYS_ADMIN bypass",
        "2.6": "Various legacy local exploits"
    }
    for key in suggestions:
        if key in kernel:
            results["kernel_exploits"].append(suggestions[key])
            console.print(f"[red][Exploit][/red] {suggestions[key]} for kernel {kernel}")


def save_report():
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    with open(f"redrootlpe_report_{ts}.json", "w") as f:
        json.dump(results, f, indent=2)
    console.print(f"\n[bold green]✔ Report saved as:[/bold green] redrootlpe_report_{ts}.json")


if __name__ == "__main__":
    animate_banner()
    redroot_header()
    get_user_info()
    get_os_info()
    find_suid_binaries()
    check_writable_configs()
    check_cron_jobs()
    sudo_privs()
    env_vars()
    parse_fstab()
    check_capabilities()
    detect_docker()
    kernel_exploit_suggestions()
    save_report()
