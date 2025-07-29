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

import time
import subprocess
from itertools import cycle
from rich.console import Console

console = Console()

# RedRoot directories (for visual loading effect)
directories = [
    "Directory-BruteForcing",
    "Packet-Capturing",
    "Password-Cracking",
    "Portscanner",
    "RedRoot-Phisher",
    "Reverse-Listener",
    "Web-Exploitation/SQL-Injection",
    "Web-Exploitation/Web-Recon",
    "Web-Exploitation/XSS-Recontion"
]

# Python packages to install
pip_packages = [
    "urllib3", "playwright", "argparse", "requests", "rich", "scapy", "bcrypt",
    "paramiko", "beautifulsoup4", "pexpect", "pymysql", "psycopg2-binary",
    "cx_Oracle", "ldap3", "pysnmp"
]

# RedRoot Banner
def print_banner():
    banner = """
[bold red]
                                          ..,;clloollc:,..                                          
                                      .,cdxl:;'......',:ldxl;.                                      
                                    ,okl,.                .,lkd;.                                    
                                  ,xx;.                      .;dx;                                   
                                .dx;  ..''..   ..''..   ..''..  ;xd.                                 
                               'kd.   .'..''   ''..''   ''..'.   .ok;                                
                              'ko.     .''..   ..''..   ..''..     lk,                               
                             .xx.       .'       ''       ''        dk.                              
                             :k;        .'.      ''      .'.        'kc                              
                             ok.         ..'.....''.....''.          kx                              
                             dk.           ......''......            dk.                             
                             ok.                 ''                 .kx                              
                             :k:                .''.                ,kl                              
                             .xk.             ..''''...            .dk.                              
                              'kd.      ..'.'''. '' ..''.'..       ok,                               
                               'xd.   ..'.  ''   ''   .'. .'..   .ok,                                 
                                .dk:   .   .'.  .''.   .'   ..  ,xd.                                 
                                  ,dx:.    ..  .'..'.   .    .;dx;                                   
                                    'lko;.     ..  ..     .;oko,                                      
                                      .,cdkoc;,'....',;coxxl,.                                        
                                          ..,;ccllllcc;,..                                            

                  [bold yellow]'llllc,  .lllll; .lllll:.  .lllll;.  .:lool:.   ;loooc' 'lllllll. [/bold yellow]                 
                  [bold yellow];kl..ckc .kx.... .kk...dk' .kx..;kx .kk,..;kx  ckc...dk' ..ok;..  [/bold yellow]                
                  [bold yellow];ko.'ok: .kkccc. .kk.  ck; .kx..ckd .kk   .kk. ok,   lk;   ok,     [/bold yellow]             
                  [bold yellow];kxlkk,  .kx.... .kk.  lk; .kk..ckl. .kk   .kk. ok,   lk;   ok,     [/bold yellow]            
                  [bold yellow];kl ;ko. .kk,,,' .kk;,;xx. .kx 'xx.  dk:''cko  ;ko,';xx.   ok,     [/bold yellow]            
                  [bold cyan].;'  ';' .;;;;;,  ;;;;;'   .;,  .;,   ';::;.    .,::;'.    ';.   [/bold cyan]
[/bold red]
"""
    console.print(banner)

# Animation setup
spinner_cycle = cycle(["◐", "◓", "◑", "◒"])
bar_width = 30

# Step 1: Print banner
print_banner()
time.sleep(1)

# Step 2: Loading animation
console.print("\n[bold red]Just RedRoot[/bold red]\n")
for i, directory in enumerate(directories, 1):
    spinner = next(spinner_cycle)
    filled_blocks = int((i / len(directories)) * bar_width)
    progress_bar = f"[cyan]{'█' * filled_blocks}{'-' * (bar_width - filled_blocks)}[/cyan]"
    line = f"{spinner} LOADING            {progress_bar}  → Processing: [bold yellow]{directory}[/bold yellow]"

    console.print(line, end="\r", highlight=False)
    time.sleep(0.4)

# Step 3: Final Load Complete
console.print(" " * console.width, end="\r")  # Clear line
final_bar = "[cyan]██████████████████████████████[/cyan]"
console.print(f"◒ LOADING            {final_bar}  → [bold red]RedRoot[/bold red] [bold yellow]Suit up Successfully[/bold yellow]")

# Step 4: Installing Dependencies
console.print("\n[bold cyan]Installing Python dependencies...[/bold cyan]\n")
for package in pip_packages:
    try:
        subprocess.run(["pip", "install", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        console.print(f"[bold cyan]✔[/bold cyan] [yellow]{package}[/yellow] installed.")
        time.sleep(0.1)
    except Exception as e:
        console.print(f"[bold red]✖ Failed:[/bold red] {package} — {e}")

# Step 5: Final Done Message
console.print("\n[bold yellow]✔[/bold yellow] [bold red]RedRoot environment setup complete![/bold red]\n")
