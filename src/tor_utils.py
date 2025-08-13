import json
import socket
from pathlib import Path
from time import sleep
import subprocess

def isTorRunning(host="127.0.0.1", port=9050):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        try:
            s.connect((host, port))
            return True
        except (socket.timeout, ConnectionRefusedError):
            return False

def start_tor():
    if isTorRunning():
        print("Tor is already runnig")
    else:
        print("Trying to start Tor")
        with open("config.json", "r") as f:
            cfg = json.load(f)
        subprocess.Popen(
            ["tor", "-f", cfg["torrc_path"]],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        sleep(5)

def send_newnym():
    COOKIE = Path("~/.tor/control_auth_cookie")
    cookie_hex = COOKIE.read_bytes().hex()
    with socket.create_connection(("127.0.0.1", 9051)) as s:
        msg = f'AUTHENTICATE {cookie_hex}\r\nSIGNAL NEWNYM\r\nQUIT\r\n'
        s.sendall(msg.encode())