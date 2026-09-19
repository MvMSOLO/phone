"""
AxtarGet Screen Mirroring V1.4 - Main CLI & Terminal Controller
Features:
 - Matrix/Terminal Green/White Theme using Rich library
 - ASCII Banner: "AxtarGet Screen Mirroring V1.4"
 - Real-time status panel (AxtarGet Server, ADB Connection, Local & Public IP/Port)
 - Interactive Command Prompt:
     ip     - Show local and Wi-Fi IP addresses
     -qr    - Generate and display QR code in terminal for mobile browser connection
     -clear - Clear terminal screen
     -exit  - Shutdown server and exit
"""

import os
import sys
import socket
import time
import threading
import uvicorn
import qrcode
from io import StringIO
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from rich import print as rprint
from rich.text import Text
from rich.style import Style

import web_app
from web_app import adb_manager

console = Console()

BANNER = r"""
[bold green]
 █████╗ ██╗  ██╗████████╗█████╗ ██████╗  ██████╗ ███████╗████████╗
██╔══██╗╚██╗██╔╝╚══██╔══╝██╔══██╗██╔══██╗██╔════╝ ██╔════╝╚══██╔══╝
███████║ ╚███╔╝    ██║   ███████║██████╔╝██║  ███╗█████╗     ██║
██╔══██║ ██╔██╗    ██║   ██╔══██║██╔══██╗██║   ██║██╔══╝     ██║
██║  ██║██╔╝ ██╗   ██║   ██║  ██║██║  ██║╚██████╔╝███████╗   ██║
╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝
[/bold green]
[bold white]   --->  SCREEN MIRRORING & REMOTE CONTROL TOOL V1.4  <---   [/bold white]
"""

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8080

def get_local_ip() -> str:
    """Retrieves the primary LAN/Wi-Fi IPv4 address of the local machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
        # Connect to a public IP to identify local routing interface
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def print_qr_code(url: str):
    """Generates and prints an ASCII QR code directly into the terminal console."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=1,
        border=1,
    )
    qr.add_data(url)
    qr.make(fit=True)

    console.print(f"\n[bold green][+] Wi-Fi Connection QR Code for URL: [bold white]{url}[/bold green]")
    f = StringIO()
    qr.print_ascii(out=f, invert=True)
    f.seek(0)
    console.print(f"[bold green]{f.read()}[/bold green]")

def build_status_panel() -> Panel:
    """Builds a Rich Panel displaying server and ADB device status."""
    devices = adb_manager.get_devices()
    local_ip = get_local_ip()

    table = Table(show_header=False, expand=True, box=None)
    table.add_column("Key", style="bold green", width=24)
    table.add_column("Value", style="bold white")

    # AxtarGet Server Status
    table.add_row("AxtarGet Server:", "[bold bright_green]● ACTIVE / RUNNING[/bold bright_green]")

    # ADB Status
    if adb_manager.is_adb_available():
        table.add_row("ADB Service:", "[bold green]ONLINE[/bold green]")
    else:
        table.add_row("ADB Service:", "[bold yellow]NOT DETECTED (System ADB missing)[/bold yellow]")

    # Devices
    if devices:
        dev_info = ", ".join([f"{d['model']} ({d['id']})" for d in devices])
        table.add_row("Connected Devices:", f"[bold green]{len(devices)} Connected[/bold green] -> [cyan]{dev_info}[/cyan]")
    else:
        table.add_row("Connected Devices:", "[bold red]0 Devices (Waiting for USB/Wi-Fi ADB...)[/bold red]")

    # URLs
    table.add_row("Local Access URL:", f"http://127.0.0.1:{SERVER_PORT}")
    table.add_row("Network Wi-Fi URL:", f"[bold bright_green]http://{local_ip}:{SERVER_PORT}[/bold bright_green]")

    return Panel(
        table,
        title="[bold green] [ STATUS & NETWORK DASHBOARD ] [/bold green]",
        border_style="green"
    )

def start_web_server():
    """Runs Uvicorn Web Server in a separate thread."""
    uvicorn.run(
        "web_app:app",
        host=SERVER_HOST,
        port=SERVER_PORT,
        log_level="error",
        access_log=False
    )

def main():
    # Start web server thread
    server_thread = threading.Thread(target=start_web_server, daemon=True)
    server_thread.start()

    # Allow server a moment to start up
    time.sleep(1)

    # Initial Screen display
    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(BANNER)
    console.print(build_status_panel())

    console.print("\n[bold green]Commands available:[/bold green] [white]'ip'[/white] (show addresses) | [white]'-qr'[/white] (show QR code) | [white]'-clear'[/white] (clean screen) | [white]'-exit'[/white] (close server)\n")

    while True:
        try:
            cmd = console.input("[bold green]AxtarGet-CLI>[/bold green] ").strip()

            if not cmd:
                continue

            if cmd == "ip":
                local_ip = get_local_ip()
                console.print(f"\n[bold green][+] Localhost URL:[/bold green] [white]http://127.0.0.1:{SERVER_PORT}[/white]")
                console.print(f"[bold green][+] LAN/Wi-Fi URL:[/bold green]  [bold bright_green]http://{local_ip}:{SERVER_PORT}[/bold bright_green]\n")

            elif cmd == "-qr":
                local_ip = get_local_ip()
                url = f"http://{local_ip}:{SERVER_PORT}"
                print_qr_code(url)

            elif cmd == "-clear":
                os.system('cls' if os.name == 'nt' else 'clear')
                console.print(BANNER)
                console.print(build_status_panel())
                console.print("\n[bold green]Commands available:[/bold green] [white]'ip'[/white] | [white]'-qr'[/white] | [white]'-clear'[/white] | [white]'-exit'[/white]\n")

            elif cmd == "-exit":
                console.print("\n[bold yellow][!] Shutting down AxtarGet Screen Mirroring V1.4... Goodbye![/bold yellow]\n")
                sys.exit(0)

            else:
                console.print(f"[bold red][!] Unknown command: '{cmd}'. Available: ip, -qr, -clear, -exit[/bold red]")

        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold yellow][!] Exiting...[/bold yellow]")
            sys.exit(0)

if __name__ == "__main__":
    main()
