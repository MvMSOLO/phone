"""
AxtarGet Screen Mirroring V2.0 - Main CLI & Terminal Controller
Features:
 - Matrix/Terminal Green/White Theme using Rich library
 - ASCII Banner: "AxtarGet Screen Mirroring V2.0 (Mobile-to-Mobile 120 FPS 4K)"
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
from rich.table import Table
from rich import print as rprint

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
[bold white]---> AXTARGET SCREEN MIRRORING V2.0 (MOBILE-TO-MOBILE 120 FPS 4K HDR) <---[/bold white]
"""

SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8080

def get_local_ip() -> str:
    """Retrieves the primary LAN/Wi-Fi IPv4 address of the local machine."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0.5)
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

    console.print(f"\n[bold green][+] Scan this QR Code on Phone B to control Phone A: [bold white]{url}[/bold green]")
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

    table.add_row("AxtarGet Server V2.0:", "[bold bright_green]● ONLINE (120 FPS 4K HDR Ready)[/bold bright_green]")

    if adb_manager.is_adb_available():
        table.add_row("ADB Engine:", "[bold green]ACTIVE[/bold green]")
    else:
        table.add_row("ADB Engine:", "[bold yellow]NOT DETECTED (System ADB missing)[/bold yellow]")

    if devices:
        dev_info = ", ".join([f"{d['model']} ({d['id']})" for d in devices])
        table.add_row("Target Smartphone:", f"[bold green]{len(devices)} Connected[/bold green] -> [cyan]{dev_info}[/cyan]")
    else:
        table.add_row("Target Smartphone:", "[bold red]0 Devices (Waiting for USB/Wi-Fi ADB...)[/bold red]")

    table.add_row("Local Access URL:", f"http://127.0.0.1:{SERVER_PORT}")
    table.add_row("Mobile Wi-Fi URL:", f"[bold bright_green]http://{local_ip}:{SERVER_PORT}[/bold bright_green]")

    return Panel(
        table,
        title="[bold green] [ AXTARGET V2.0 DASHBOARD ] [/bold green]",
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
    server_thread = threading.Thread(target=start_web_server, daemon=True)
    server_thread.start()

    time.sleep(1)

    os.system('cls' if os.name == 'nt' else 'clear')
    console.print(BANNER)
    console.print(build_status_panel())

    console.print("\n[bold green]Commands:[/bold green] [white]'ip'[/white] (addresses) | [white]'-qr'[/white] (mobile QR code) | [white]'-clear'[/white] (clear screen) | [white]'-exit'[/white] (exit)\n")

    while True:
        try:
            cmd = console.input("[bold green]AxtarGet-CLI-V2.0>[/bold green] ").strip()

            if not cmd:
                continue

            if cmd == "ip":
                local_ip = get_local_ip()
                console.print(f"\n[bold green][+] Localhost URL:[/bold green] [white]http://127.0.0.1:{SERVER_PORT}[/white]")
                console.print(f"[bold green][+] Wi-Fi Mobile URL:[/bold green] [bold bright_green]http://{local_ip}:{SERVER_PORT}[/bold bright_green]\n")

            elif cmd == "-qr":
                local_ip = get_local_ip()
                url = f"http://{local_ip}:{SERVER_PORT}"
                print_qr_code(url)

            elif cmd == "-clear":
                os.system('cls' if os.name == 'nt' else 'clear')
                console.print(BANNER)
                console.print(build_status_panel())
                console.print("\n[bold green]Commands:[/bold green] [white]'ip'[/white] | [white]'-qr'[/white] | [white]'-clear'[/white] | [white]'-exit'[/white]\n")

            elif cmd == "-exit":
                console.print("\n[bold yellow][!] Exiting AxtarGet Screen Mirroring V2.0... Goodbye![/bold yellow]\n")
                sys.exit(0)

            else:
                console.print(f"[bold red][!] Unknown command: '{cmd}'. Available: ip, -qr, -clear, -exit[/bold red]")

        except (KeyboardInterrupt, EOFError):
            console.print("\n[bold yellow][!] Exiting...[/bold yellow]")
            sys.exit(0)

if __name__ == "__main__":
    main()
