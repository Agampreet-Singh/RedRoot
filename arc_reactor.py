# Copyright 2025 Agampreet Singh
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
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
import os
import time
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()

ARC_REACTOR = r"""
                                              ........                                              
                                       .:::::::......:::::::.                                       
                                      =-                   .=:                                      
                               .---    -:                  -:   :--:                                 
                             :-:  :=    -:                -:   :-  :-:                               
                           :-.     .=    -:              -:   :-     .--                             
                         .-.        .=    --            =:   :-        .-:                           
                        -+:::::::::::-=    --..........=.   -=:::::::::.:==                          
                                            ...........       ........... .                          
                           .   ..............          ...... .....     .                            
                         .:==-:.....................................::==-:.                          
                     -.  :+-::::.                                 .:::::==   .:                      
                    --=.  :=.:-::-::............................:--:--::=   :==:                     
                   .= .=.  :-  .:-::.::......................::.:-::  .=   :=  =                     
                   =.  .=.  :=    .-.  .:.::::::::::::::::.:   --    :=   :=   :-                    
                   =     =.  .=     =: .=.                -=  -:    :-   :=    .=                    
                  .-      =.  .=     -: .=               :-  =:    :-   :-      =                    
                  :-      .=.  .=.    -: .=.            :-  =:    :-   :=       =                    
                  .-:::::::::   .=.    -- .=.          :-  =.    --    -::::::::-                    
                                 .=.    -- .=.        --  =.    --                                   
                  :-::::::::::--   =.    :-  =.      -- .=.    -:   --::::::::::=:                   
                  .=           :-   =.    :-  =.    -: .=.    -:   =:           =.                   
                   =.           :=   =:    :=  =:  -: .=     =:   =:           .=                    
                   .=            :=   -:    .=  =:-: :=     =:  .=.            =.                    
                    --            .=   -:    .=  -: :=     =.  .=.            -:                    
                     -:            :=   -:    .=.  :-     =.   =:            --                     
                      -:          .=.    --    .= :-    .=.     =.          --                      
                       --        .=.      --    =.-.   .=.       =.        -:                       
                        :=.     .=    -=   --   =.-.  .=.  .==    =:     :=.                         
                          --   .=    =..=   :-  =.-. .=   .=..=.   =:  .-:                           
                           .--:=   .=.  .=.  :- =.-..=   .=   .=.   ----                            
                             .:   .=.    .=.  :-=.--=   :=      =.   :                               
                                  =:       =.  .*.==   :=       :=                                  
                                   :--:.    -:  . .   :-   ..:-:.                                    
                                      ..:::::+:      :+:::::.                                        
"""

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def animate_banner():
    clear()
    console.print(Text("Welcome Mr. Agampreet", style="bold red"), justify="center")
    time.sleep(0.5)
    console.print(f"[bold cyan]{ARC_REACTOR}[/bold cyan]")
    time.sleep(1)

# ============== MODULE STATUS DISPLAY ==============

# Public modules
ACTIVE_MODULES = {
    "Directory-BruteForcing": "🗂",
    "Packet-Capturing": "📡",
    "Portscanner": "📌",
    "RedRoot-Exploits": "🎯",
    "Reverse-Listener": "🎧"
}

# Locked/private modules
LOCKED_MODULES = {
    "Payload-Generator": "💣",
    "Password-Cracking": "🔐",
    "Privilege-Escalation": "📈",
    "RedRoot-Backdoor": "🕳",
    "RedRoot-DOS": "💥",
    "RedRoot-EvilTwin": "📶",
    "RedRoot-Phisher": "🎣",
    "SMB-Enum": "📂",
    "Web-Exploitation": "🌐"
}

def show_module_table():
    table = Table(title="RedRoot Lite :: Module Status", style="bold magenta")
    table.add_column("Module", style="bold cyan")
    table.add_column("Status", justify="center")

    # Show active modules
    for module, icon in ACTIVE_MODULES.items():
        table.add_row(f"{icon} {module}", "[green]✔ Active[/green]")

    # Show locked modules
    for module, icon in LOCKED_MODULES.items():
        table.add_row(f"{icon} {module}", "[red]🔒 Locked – Private Module[/red]")

    console.print(table)

# ============== MAIN ==============

def main():
    animate_banner()
    show_module_table()
    console.print("\n[bold yellow]Choose an active module to launch or type 'exit' to quit.[/bold yellow]")

if __name__ == "__main__":
    main()
