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
from scapy.all import sniff, IP, TCP, UDP, ICMP, wrpcap
import argparse
from datetime import datetime
import os
import time
from rich.console import Console
from rich.text import Text

console = Console()
captured_packets = []

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

# ------------------------ Packet Parsing ------------------------
def parse_packet(pkt):
    timestamp = datetime.now().strftime('%H:%M:%S')
    if IP in pkt:
        ip_layer = pkt[IP]
        src = ip_layer.src
        dst = ip_layer.dst
        proto = 'OTHER'
        length = len(pkt)

        if TCP in pkt:
            proto = "[blue]TCP[/blue]"
        elif UDP in pkt:
            proto = "[green]UDP[/green]"
        elif ICMP in pkt:
            proto = "[magenta]ICMP[/magenta]"

        console.print(f"[{timestamp}] {src} -> {dst} | {proto} | {length} bytes")
        captured_packets.append(pkt)

# ------------------------ Sniffer Logic ------------------------
def start_sniff(interface, count, proto_filter, bpf_filter, save_path):
    console.print(f"[*] Sniffing on [bold cyan]{interface}[/bold cyan] | Protocol: [bold yellow]{proto_filter.upper()}[/bold yellow] | Count: [bold yellow]{count or '∞'}[/bold yellow]")
    if bpf_filter:
        console.print(f"[*] BPF Filter: [bold green]{bpf_filter}[/bold green]")

    def filter_fn(pkt):
        if proto_filter == 'all':
            return IP in pkt
        elif proto_filter == 'tcp':
            return TCP in pkt
        elif proto_filter == 'udp':
            return UDP in pkt
        elif proto_filter == 'icmp':
            return ICMP in pkt
        return False

    try:
        sniff(
            iface=interface,
            prn=parse_packet,
            lfilter=filter_fn,
            filter=bpf_filter if bpf_filter else None,
            count=count if count > 0 else 0,
            store=False
        )
    except Exception as e:
        console.print(f"[!] Error: {e}", style="bold red")

    if save_path and captured_packets:
        wrpcap(save_path, captured_packets)
        console.print(f"[+] Saved {len(captured_packets)} packets to [bold green]{save_path}[/bold green]")

# ------------------------ Main ------------------------
if __name__ == '__main__':
    animate_typing_banner()

    parser = argparse.ArgumentParser(description='Extended TCPDUMP-like Packet Sniffer')
    parser.add_argument('--iface', required=True, help='Interface to sniff on (e.g., eth0)')
    parser.add_argument('--count', type=int, default=0, help='Number of packets to capture (0 = unlimited)')
    parser.add_argument('--proto', choices=['tcp', 'udp', 'icmp', 'all'], default='all', help='Protocol filter')
    parser.add_argument('--bpf', default='', help='BPF-style filter (e.g., "port 80")')
    parser.add_argument('--save', help='Path to save captured packets as .pcap')
    args = parser.parse_args()

    try:
        start_sniff(args.iface, args.count, args.proto, args.bpf, args.save)
    except KeyboardInterrupt:
        console.print("\n[!] Stopped by user.", style="bold red")
