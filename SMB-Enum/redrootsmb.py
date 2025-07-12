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
import json
import csv
import os
import io
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from impacket.smbconnection import SMBConnection, SessionError
from impacket.dcerpc.v5 import samr, lsad
from impacket.dcerpc.v5.dtypes import MAXIMUM_ALLOWED
from rich.console import Console
from rich.text import Text
from colorama import init

# Initialize colorama for Windows
init(autoreset=True)

# Global setup
console = Console()
results = {
    "shares": [],
    "users": [],
    "groups": [],
    "policies": {},
    "writable_shares": [],
}

# Clear terminal
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# Animated welcome banner
def animate_typing_banner():
    clear()
    message = "Welcome Mr. Agampreet"
    colors = ["red", "gold1"]
    styled_text = Text()
    for i, char in enumerate(message):
        color = colors[i % 2]
        styled_text.append(char, style=f"bold {color}")
        console.print(styled_text, end="\r", soft_wrap=True)
        time.sleep(0.05)
    console.print()
    time.sleep(0.2)

# RedRoot banner
def redroot_banner():
    console.print("\n[bold red]⛓ REDROOT SMB ENUMERATOR[/bold red]", justify="center")
    console.print("[cyan]Advanced SMB Enumeration with Write Access, SAM Dump, and Reporting[/cyan]\n", justify="center")

# Check read/write access
def check_share_access(smb_client, share_name):
    access = {"read": False, "write": False}
    try:
        smb_client.listPath(share_name, "*")
        access["read"] = True
    except Exception:
        pass

    try:
        test_file = "redroot_test.txt"
        smb_client.putFile(share_name, test_file, io.BytesIO(b"RedRoot Test"))
        smb_client.deleteFile(share_name, test_file)
        access["write"] = True
        results["writable_shares"].append(share_name)
    except Exception:
        pass
    return access

# List files (threaded)
def list_files_in_share(smb_client, share_name):
    try:
        files = smb_client.listPath(share_name, '*')
        return [file.get_longname() for file in files]
    except Exception:
        return []

# Enumerate users
def dump_users(smb_client):
    try:
        rpctransport = smb_client.get_dce_rpc()
        samr_conn = samr.hSamrConnect(rpctransport)
        domains = samr.hSamrEnumerateDomainsInSamServer(samr_conn)['Buffer']['Buffer']
        domain_name = domains[0]['Name']
        domain_handle = samr.hSamrOpenDomain(samr_conn, MAXIMUM_ALLOWED,
            domainId=samr.hSamrLookupDomainInSamServer(samr_conn, domain_name)['DomainId'])

        user_info = samr.hSamrEnumerateUsersInDomain(samr_conn, domain_handle)['Buffer']['Buffer']
        for user in user_info:
            username = user['Name']
            results["users"].append(username)
            console.print(f"[green][+][/green] User: {username}")
    except Exception as e:
        console.print(f"[red][-] Failed to enumerate users: {e}[/red]")

# Enumerate groups
def dump_groups(smb_client):
    try:
        rpctransport = smb_client.get_dce_rpc()
        samr_conn = samr.hSamrConnect(rpctransport)
        domains = samr.hSamrEnumerateDomainsInSamServer(samr_conn)['Buffer']['Buffer']
        domain_name = domains[0]['Name']
        domain_handle = samr.hSamrOpenDomain(samr_conn, MAXIMUM_ALLOWED,
            domainId=samr.hSamrLookupDomainInSamServer(samr_conn, domain_name)['DomainId'])

        group_info = samr.hSamrEnumerateGroupsInDomain(samr_conn, domain_handle)['Buffer']['Buffer']
        for group in group_info:
            groupname = group['Name']
            results["groups"].append(groupname)
            console.print(f"[blue][+][/blue] Group: {groupname}")
    except Exception as e:
        console.print(f"[red][-] Failed to enumerate groups: {e}[/red]")

# Password policy
def get_password_policy(smb_client):
    try:
        lsa_handle = lsad.hLsarOpenPolicy2(smb_client, lsad.POLICY_VIEW_LOCAL_INFORMATION)
        policy_info = lsad.hLsarQueryInformationPolicy2(lsa_handle, lsad.POLICY_ACCOUNT_DOMAIN_INFORMATION)
        domain_name = policy_info['PolicyAccountDomainInfo']['DomainName']['Buffer']
        sid = policy_info['PolicyAccountDomainInfo']['DomainSid']['Data'].hex()
        results["policies"]["domain_name"] = domain_name
        results["policies"]["domain_sid"] = sid
        console.print(f"[cyan][+][/cyan] Domain: {domain_name} | SID: {sid}")
    except Exception as e:
        console.print(f"[red][-] Failed to get policy: {e}[/red]")

# SAM hash dump placeholder
def dump_sam_hashes(smb_client):
    try:
        if 'ADMIN$' not in [s['shi1_netname'][:-1] for s in smb_client.listShares()]:
            console.print("[yellow][!][/yellow] ADMIN$ share not found. Can't dump SAM.")
            return

        console.print("[magenta][*][/magenta] Trying to dump SAM using ADMIN$... (Not fully implemented)")
        # Placeholder — full implementation would require secretsdump logic
    except Exception as e:
        console.print(f"[red][-] SAM dump failed: {e}[/red]")

# Save results
def save_reports(target):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    base = f"smb_enum_{target}_{timestamp}"
    
    with open(f"{base}.json", "w") as jf:
        json.dump(results, jf, indent=2)
    with open(f"{base}.csv", "w", newline='') as cf:
        writer = csv.writer(cf)
        writer.writerow(["Share", "Read", "Write"])
        for share in results["shares"]:
            writer.writerow([share['name'], share['read'], share['write']])
    console.print(f"[bold green][✓][/bold green] Reports saved to [cyan]{base}.json[/cyan] and [cyan]{base}.csv[/cyan]")

# Main enum logic
def enum_smb(target, username="", password="", domain="", port=445):
    animate_typing_banner()
    redroot_banner()
    try:
        smb_client = SMBConnection(target, target, sess_port=port)
        smb_client.login(username, password, domain)
        console.print(f"[bold green][✓][/bold green] Login successful to {target}")

        shares = smb_client.listShares()
        console.print(f"[bold yellow][*][/bold yellow] Enumerating {len(shares)} shares...\n")

        with ThreadPoolExecutor(max_workers=10) as executor:
            for share in shares:
                name = share['shi1_netname'][:-1]
                access = check_share_access(smb_client, name)
                results["shares"].append({
                    "name": name,
                    "read": access["read"],
                    "write": access["write"]
                })
                console.print(f"  [white]Share:[/white] {name} | [green]Read:[/green] {access['read']} | [red]Write:[/red] {access['write']}")
                executor.submit(list_files_in_share, smb_client, name)

        console.print("\n[bold yellow][*][/bold yellow] Enumerating users and groups...\n")
        dump_users(smb_client)
        dump_groups(smb_client)
        get_password_policy(smb_client)
        dump_sam_hashes(smb_client)

        save_reports(target)
        smb_client.close()

    except SessionError as se:
        console.print(f"[red][!] SMB Session Error: {se}[/red]")
    except Exception as e:
        console.print(f"[red][!] General Error: {e}[/red]")

# CLI args
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="🧨 RedRoot SMB Enumeration Tool")
    parser.add_argument("target", help="Target IP or hostname")
    parser.add_argument("-u", "--username", default="", help="Username")
    parser.add_argument("-p", "--password", default="", help="Password")
    parser.add_argument("-d", "--domain", default="", help="Domain")
    parser.add_argument("-P", "--port", type=int, default=445, help="SMB port")
    args = parser.parse_args()

    enum_smb(args.target, args.username, args.password, args.domain, args.port)
