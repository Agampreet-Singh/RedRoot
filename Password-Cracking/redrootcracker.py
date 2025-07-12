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
import argparse
import hashlib
import os
import pickle
import re
import subprocess
import time
import zipfile
from itertools import product
from rich.console import Console
from rich.table import Table
from rich.text import Text

console = Console()

SUPPORTED_HASHES = ['md5', 'sha1', 'sha256', 'sha512', 'ntlm', 'bcrypt']
MASK_MAP = {'?l': 'abcdefghijklmnopqrstuvwxyz', '?u': 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', '?d': '0123456789', '?s': '!@#$%^&*()'}

# ------------------ RedRoot Style ------------------

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def animate_typing_banner():
    clear()
    message = "Welcome Mr. Agampreet"
    colors = ["red", "gold1"]
    styled_text = Text()
    for i, char in enumerate(message):
        color = colors[i % len(colors)]
        styled_text.append(char, style=f"bold {color}")
        console.print(styled_text, end="\r", soft_wrap=True)
        time.sleep(0.02)
    console.print("\n")
    time.sleep(0.2)

# ------------------ Hashing Utilities ------------------

def detect_hash_type(h):
    if h.startswith('$2a$') or h.startswith('$2b$'):
        return 'bcrypt'
    return {
        32: 'md5',
        40: 'sha1',
        64: 'sha256',
        128: 'sha512'
    }.get(len(h), 'ntlm')

def compute_hash(algo, word):
    if algo == 'ntlm':
        return hashlib.new('md4', word.encode('utf-16le')).hexdigest()
    elif algo == 'bcrypt':
        import bcrypt
        return bcrypt.hashpw(word.encode(), bcrypt.gensalt()).decode()
    else:
        h = hashlib.new(algo)
        h.update(word.encode())
        return h.hexdigest()

def save_session(file, data):
    with open(file, 'wb') as f:
        pickle.dump(data, f)

def load_session(file):
    try:
        with open(file, 'rb') as f:
            return pickle.load(f)
    except:
        return {}

def benchmark(algorithm, duration=5):
    console.print(f"[bold yellow][+] Benchmarking {algorithm} for {duration} seconds...[/bold yellow]")
    count = 0
    start = time.time()
    while time.time() - start < duration:
        compute_hash(algorithm, 'test')
        count += 1
    console.print(f"[bold green][+] {count} hashes/second[/bold green]")

# ------------------ Cracking Techniques ------------------

def dictionary_attack(hashes, wordlist, algo, session, session_file):
    console.print("[cyan][*] Starting dictionary attack...[/cyan]")
    with open(wordlist, 'r', encoding='utf-8', errors='ignore') as f:
        for word in f:
            word = word.strip()
            if algo == 'bcrypt':
                import bcrypt
                for h in hashes:
                    if h not in session:
                        try:
                            if bcrypt.checkpw(word.encode(), h.encode()):
                                console.print(f"[bold green][+] Cracked: {h} -> {word}[/bold green]")
                                session[h] = word
                                save_session(session_file, session)
                        except:
                            continue
            else:
                hashed = compute_hash(algo, word)
                if hashed in hashes and hashed not in session:
                    console.print(f"[bold green][+] Cracked: {hashed} -> {word}[/bold green]")
                    session[hashed] = word
                    save_session(session_file, session)

def brute_force_attack(hashes, algo, charset, maxlen, session, session_file):
    console.print(f"[cyan][*] Starting brute-force attack (max length: {maxlen})...[/cyan]")
    for l in range(1, maxlen + 1):
        for word in product(charset, repeat=l):
            guess = ''.join(word)
            hashed = compute_hash(algo, guess)
            if hashed in hashes and hashed not in session:
                console.print(f"[bold green][+] Cracked: {hashed} -> {guess}[/bold green]")
                session[hashed] = guess
                save_session(session_file, session)

def mask_attack(hashes, algo, mask, session, session_file):
    console.print(f"[cyan][*] Starting mask attack with pattern: {mask}[/cyan]")
    charsets = [MASK_MAP.get(token, token) for token in re.findall(r'\?\w', mask)]
    pool = ['']
    for charset in charsets:
        pool = [p + c for p in pool for c in charset]
    for guess in pool:
        hashed = compute_hash(algo, guess)
        if hashed in hashes and hashed not in session:
            console.print(f"[bold green][+] Cracked: {hashed} -> {guess}[/bold green]")
            session[hashed] = guess
            save_session(session_file, session)

def rule_based_attack(hashes, wordlist, algo, session, session_file):
    console.print("[cyan][*] Starting rule-based attack...[/cyan]")
    with open(wordlist, 'r', encoding='utf-8', errors='ignore') as f:
        for word in f:
            word = word.strip()
            mutations = [word, word.upper(), word.capitalize(), word[::-1]]
            for m in mutations:
                hashed = compute_hash(algo, m)
                if hashed in hashes and hashed not in session:
                    console.print(f"[bold green][+] Cracked: {hashed} -> {m}[/bold green]")
                    session[hashed] = m
                    save_session(session_file, session)

def incremental_attack(hashes, algo, session, session_file):
    charset = 'etaoinshrdlucmfwypvbgkqjxz0123456789'
    console.print("[cyan][*] Starting incremental attack (length 1–5)...[/cyan]")
    for l in range(1, 6):
        for word in product(charset, repeat=l):
            guess = ''.join(word)
            hashed = compute_hash(algo, guess)
            if hashed in hashes and hashed not in session:
                console.print(f"[bold green][+] Cracked: {hashed} -> {guess}[/bold green]")
                session[hashed] = guess
                save_session(session_file, session)

# ------------------ ZIP Password Cracker ------------------

def zip_crack(zip_path, wordlist):
    console.print("[cyan][*] Starting ZIP password cracking...[/cyan]")
    if not zipfile.is_zipfile(zip_path):
        console.print("[bold red][!] Invalid ZIP file.[/bold red]")
        return
    with zipfile.ZipFile(zip_path) as zf:
        for word in open(wordlist, 'r', encoding='utf-8', errors='ignore'):
            password = word.strip().encode('utf-8')
            try:
                zf.extractall(pwd=password)
                console.print(f"[bold green][+] Cracked ZIP Password: {password.decode()}[/bold green]")
                return
            except:
                continue
    console.print("[bold red][!] Password not found in wordlist.[/bold red]")

# ------------------ Hash Extraction ------------------

def extract_shadow(passwd_file, shadow_file, out='merged.hashes'):
    subprocess.run(['unshadow', passwd_file, shadow_file], stdout=open(out, 'w'))
    console.print(f"[bold green][+] Merged UNIX hashes into {out}[/bold green]")

def extract_sam(system, sam, out='sam.hashes'):
    subprocess.run(['samdump2', sam, system], stdout=open(out, 'w'))
    console.print(f"[bold green][+] Extracted Windows hashes to {out}[/bold green]")

# ------------------ MAIN ------------------

def main():
    animate_typing_banner()
    console.rule("[bold red]RedRoot - Password Cracker[/bold red]")

    parser = argparse.ArgumentParser(description='RedRoot Ultimate Password Cracker')
    parser.add_argument('--hashfile', help='File with hashes')
    parser.add_argument('--algorithm', help='Hash type (or auto)')
    parser.add_argument('--dictionary', help='Wordlist file')
    parser.add_argument('--brute', action='store_true')
    parser.add_argument('--mask', help='Mask attack e.g., ?l?l?d?d')
    parser.add_argument('--rules', action='store_true')
    parser.add_argument('--incremental', action='store_true')
    parser.add_argument('--charset', default='abc123', help='Charset for brute-force')
    parser.add_argument('--maxlen', type=int, default=4)
    parser.add_argument('--session', help='Save/load cracked session')
    parser.add_argument('--show', action='store_true')
    parser.add_argument('--test', action='store_true')
    parser.add_argument('--extract-shadow', nargs=2, metavar=('passwd','shadow'))
    parser.add_argument('--extract-sam', nargs=2, metavar=('system','sam'))
    parser.add_argument('--zipfile', help='Encrypted ZIP file')
    parser.add_argument('--zip-dict', help='Wordlist for ZIP file')

    args = parser.parse_args()

    if args.extract_shadow:
        extract_shadow(args.extract_shadow[0], args.extract_shadow[1])
        return

    if args.extract_sam:
        extract_sam(args.extract_sam[0], args.extract_sam[1])
        return

    if args.zipfile and args.zip_dict:
        zip_crack(args.zipfile, args.zip_dict)
        return

    if args.test and args.algorithm:
        benchmark(args.algorithm)
        return

    session = load_session(args.session) if args.session else {}

    if args.show:
        if not session:
            console.print("[bold red][!] No session found.[/bold red]")
        else:
            console.rule("[bold cyan]Recovered Passwords[/bold cyan]")
            for h, p in session.items():
                console.print(f"[bold green]{h} -> {p}[/bold green]")
        return

    if not args.hashfile or not args.algorithm:
        console.print("[bold red][!] --hashfile and --algorithm are required for cracking.[/bold red]")
        return

    hashes = [h.strip() for h in open(args.hashfile)]
    algo = args.algorithm if args.algorithm != 'auto' else detect_hash_type(hashes[0])

    if args.dictionary:
        dictionary_attack(hashes, args.dictionary, algo, session, args.session)

    if args.rules and args.dictionary:
        rule_based_attack(hashes, args.dictionary, algo, session, args.session)

    if args.brute:
        brute_force_attack(hashes, algo, args.charset, args.maxlen, session, args.session)

    if args.mask:
        mask_attack(hashes, algo, args.mask, session, args.session)

    if args.incremental:
        incremental_attack(hashes, algo, session, args.session)

if __name__ == '__main__':
    main()
