import os
import time
import threading
import subprocess
from rich.console import Console
from rich.progress import Progress, BarColumn, TimeElapsedColumn
from rich.panel import Panel

# ---------- CONFIG -----------

# Pip libraries to install
pip_packages = [
    "urllib3", "playwright", "argparse", "requests", "rich", "scapy", "bcrypt",
    "paramiko", "beautifulsoup4", "pexpect", "pymysql", "psycopg2-binary",
    "cx_Oracle", "ldap3", "pysnmp"
]

# APT packages to install
apt_packages = ["nmap"]

# ---------- LOGIC -----------

console = Console()

def print_banner():
    try:
        # Custom ASCII art banner with colors
        banner = """
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
                                                                                                    
                                                                                                    
                  'llllc,  .lllll; .lllll:.  .lllll;.  .:lool:.   ;loooc' 'lllllll.                 
                  ;kl..ckc .kx.... .kk...dk' .kx..;kx .kk,..;kx  ckc...dk' ..ok;..                  
                  ;ko.'ok: .kkccc. .kk.  ck; .kx..ckd .kk   .kk. ok,   lk;   ok,                    
                  ;kxlkk,  .kx.... .kk.  lk; .kk..ckl. .kk   .kk. ok,   lk;   ok,                    
                  ;kl ;ko. .kk,,,' .kk;,;xx. .kx 'xx.  dk:''cko  ;ko,';xx.   ok,                    
                  .;'  ';' .;;;;;,  ;;;;;'   .;,  .;,   ';::;.    .,::;'.    ';.      
        """
        title = "[bold yellow]Just RedRoot[/bold yellow]"

        # Print the banner with colors using rich.console
        console.print(f"[bold red]{banner}[/bold red]")
        console.print(f"[bold yellow]{title}[/bold yellow]", style="bold cyan")
    except Exception as e:
        console.print(f"[red]Banner creation failed:[/red] {e}")

def install_packages():
    for pkg in pip_packages:
        subprocess.run(["pip", "install", pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    subprocess.run(["sudo", "apt", "update"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for pkg in apt_packages:
        subprocess.run(["sudo", "apt", "install", "-y", pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def run_additional_commands():
    try:
        # Redirect stdout to suppress directory processing output
        with open(os.devnull, 'w') as devnull:
            # Running the commands for setting up the necessary directories
            directories = [
                "Directory-BruteForcing", "Packet-Capturing", "Password-Cracking",
                "Portscanner", "RedRoot-Phisher", "Reverse-Listener", "Web-Exploitation",
                "SQL-Injection", "Web-Recon", "XSS"
            ]
            for dir in directories:
                if os.path.isdir(dir):  # Check if the directory exists
                    console.print(f"[bold green]Processing directory: {dir}[/bold green]")
                    os.chdir(dir)
                    
                    # Handle specific Web-Exploitation subdirectories
                    if dir == "Web-Exploitation":
                        # If we're inside 'Web-Exploitation', process its subdirectories.
                        web_exploitation_subdirs = ["SQL-Injection", "Web-Recon", "XSS"]
                        for subdir in web_exploitation_subdirs:
                            if os.path.isdir(subdir):
                                console.print(f"[bold blue]Entering Web-Exploitation/{subdir}[/bold blue]")
                                os.chdir(subdir)
                                subprocess.run("chmod +x *", shell=True)
                                if subdir == "SQL-Injection":
                                    subprocess.run("cp -r redrootsqli.py /usr/lib/python3.13/", shell=True)
                                    subprocess.run("cp -r redrootsqli /usr/local/bin/", shell=True)
                                elif subdir == "Web-Recon":
                                    subprocess.run("cp -r redrootwr.py /usr/lib/python3.13/", shell=True)
                                    subprocess.run("cp -r redrootwr /usr/local/bin/", shell=True)
                                elif subdir == "XSS":
                                    subprocess.run("cp -r redrootxss.py /usr/lib/python3.13/", shell=True)
                                    subprocess.run("cp -r redrootxss /usr/local/bin/", shell=True)
                                os.chdir("..")  # Return to Web-Exploitation directory
                    else:
                        subprocess.run("chmod +x *", shell=True)
                        if dir == "Directory-BruteForcing":
                            subprocess.run("cp -r redrootdir.py /usr/lib/python3.13/", shell=True)
                            subprocess.run("cp -r redrootdir /usr/local/bin/", shell=True)
                        elif dir == "Packet-Capturing":
                            subprocess.run("cp -r redrootpcap.py /usr/lib/python3.13/", shell=True)
                            subprocess.run("cp -r redrootpcap /usr/local/bin/", shell=True)
                        elif dir == "Password-Cracking":
                            subprocess.run("cp -r redrootcracker.py /usr/lib/python3.13/", shell=True)
                            subprocess.run("cp -r redrootservice.py /usr/lib/python3.13/", shell=True)
                            subprocess.run("cp -r redrootcracker /usr/local/bin/", shell=True)
                            subprocess.run("cp -r redrootservice /usr/local/bin/", shell=True)
                        elif dir == "Portscanner":
                            subprocess.run("cp -r redrootps.py /usr/lib/python3.13/", shell=True)
                            subprocess.run("cp -r redrootps /usr/local/bin/", shell=True)
                        elif dir == "RedRoot-Phisher":
                            subprocess.run("cp -r auth /usr/local/bin/", shell=True)
                            subprocess.run("cp -r .git /usr/local/bin/", shell=True)
                            subprocess.run("cp -r .github /usr/local/bin/", shell=True)
                            subprocess.run("cp -r redrootfisher.sh /usr/local/bin/", shell=True)
                            subprocess.run("cp -r /usr/local/bin/redrootfisher.sh /usr/local/bin/redrootfisher", shell=True)
                            subprocess.run("cp -r scripts /usr/local/bin/", shell=True)
                            subprocess.run("cp -r .server /usr/local/bin/", shell=True)
                            subprocess.run("cp -r .sites /usr/local/bin/", shell=True)
                        elif dir == "Reverse-Listener":
                            subprocess.run("cp -r redrootlistener.py /usr/lib/python3.13/", shell=True)
                            subprocess.run("cp -r redrootlistener /usr/local/bin/", shell=True)
                        os.chdir("..")
                else:
                    console.print(f"[red]Directory {dir} not found, skipping...[/red]")
    except Exception as e:
        console.print(f"[red]Error in running commands: {e}[/red]")

def loading_bar():
    with Progress("[progress.description]{task.description}", BarColumn(), TimeElapsedColumn()) as progress:
        task = progress.add_task("Installing dependencies...", total=100)
        for i in range(100):
            progress.update(task, advance=1)
            time.sleep(0.07)  # simulate time

def main():
    print_banner()
    t1 = threading.Thread(target=install_packages)
    t2 = threading.Thread(target=loading_bar)
    t3 = threading.Thread(target=run_additional_commands)
    t1.start()
    t2.start()
    t3.start()
    t1.join()
    t2.join()
    t3.join()
    console.print("[bold green]✅ Installation Complete! RedRoot is ready to use.[/bold green]")

if __name__ == "__main__":
    main()
