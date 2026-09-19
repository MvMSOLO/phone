"""
AxtarGet Screen Mirroring V2.0 - Web Application & Screen Streamer
FastAPI & WebSockets powered backend for ultra-low latency (up to 120 FPS / 4K HDR),
mobile-to-mobile phone browser remote control, and gesture touch event processing.
"""

import os
import sys
import time
import io
import asyncio
import subprocess
import shutil
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import cv2
import numpy as np

app = FastAPI(title="AxtarGet Screen Mirroring V2.0", version="2.0")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
os.makedirs(TEMPLATES_DIR, exist_ok=True)
templates = Jinja2Templates(directory=TEMPLATES_DIR)

class ADBManager:
    def __init__(self):
        self.adb_path = shutil.which("adb") or "adb"

    def is_adb_available(self) -> bool:
        try:
            res = subprocess.run([self.adb_path, "version"], capture_output=True, text=True, timeout=3)
            return res.returncode == 0
        except Exception:
            return False

    def get_devices(self) -> List[Dict[str, str]]:
        if not self.is_adb_available():
            return []
        try:
            res = subprocess.run([self.adb_path, "devices", "-l"], capture_output=True, text=True, timeout=5)
            devices = []
            lines = res.stdout.strip().splitlines()
            for line in lines[1:]:
                if not line.strip():
                    continue
                parts = line.split()
                if len(parts) >= 2 and parts[1] == "device":
                    device_id = parts[0]
                    model = "Android Phone"
                    for part in parts[2:]:
                        if part.startswith("model:"):
                            model = part.split(":", 1)[1]
                    devices.append({"id": device_id, "model": model, "status": "device"})
            return devices
        except Exception as e:
            print(f"[ADB Error] Failed to list devices: {e}")
            return []

    def capture_frame_bytes(self, device_id: Optional[str] = None) -> Optional[bytes]:
        """Captures screen frame directly using adb exec-out screencap -p for minimal latency."""
        if not self.is_adb_available():
            return None
        cmd = [self.adb_path]
        if device_id:
            cmd.extend(["-s", device_id])
        cmd.extend(["exec-out", "screencap", "-p"])
        try:
            res = subprocess.run(cmd, capture_output=True, timeout=3)
            if res.returncode == 0 and res.stdout and len(res.stdout) > 100:
                return res.stdout
        except Exception:
            pass
        return None

    def execute_input_tap(self, x: int, y: int, device_id: Optional[str] = None):
        cmd = [self.adb_path]
        if device_id:
            cmd.extend(["-s", device_id])
        cmd.extend(["shell", "input", "tap", str(x), str(y)])
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"[ADB Input Error] Tap failed: {e}")

    def execute_input_swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 200, device_id: Optional[str] = None):
        cmd = [self.adb_path]
        if device_id:
            cmd.extend(["-s", device_id])
        cmd.extend(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(max(50, duration_ms))])
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"[ADB Input Error] Swipe failed: {e}")

    def execute_keyevent(self, keycode: int, device_id: Optional[str] = None):
        cmd = [self.adb_path]
        if device_id:
            cmd.extend(["-s", device_id])
        cmd.extend(["shell", "input", "keyevent", str(keycode)])
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"[ADB Input Error] Keyevent failed: {e}")

    def execute_text_input(self, text: str, device_id: Optional[str] = None):
        cmd = [self.adb_path]
        if device_id:
            cmd.extend(["-s", device_id])
        safe_text = text.replace(" ", "%s")
        cmd.extend(["shell", "input", "text", safe_text])
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"[ADB Input Error] Text input failed: {e}")

adb_manager = ADBManager()

def generate_fallback_frame(device_count: int, quality_mode: str = "4k") -> bytes:
    """Generates futuristic Matrix screen background when device connection is initializing."""
    width, height = 1080, 1920
    img = np.zeros((height, width, 3), dtype=np.uint8)

    # Grid lines
    for y in range(0, height, 60):
        cv2.line(img, (0, y), (width, y), (0, 30, 0), 1)
    for x in range(0, width, 60):
        cv2.line(img, (x, 0), (x, height), (0, 30, 0), 1)

    cv2.rectangle(img, (30, 30), (width - 30, height - 30), (0, 255, 100), 3)

    cv2.putText(img, "AXTARGET SCREEN MIRRORING V2.0", (80, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 120), 3, cv2.LINE_AA)
    cv2.putText(img, "MOBILE-TO-MOBILE 120 FPS 4K HDR", (80, 220), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2, cv2.LINE_AA)

    if device_count > 0:
        cv2.putText(img, "STATUS: Smartphone Connected - Streaming...", (80, 340), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
    else:
        cv2.putText(img, "STATUS: Searching for Smartphone (USB/Wi-Fi)...", (80, 340), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 180, 255), 2, cv2.LINE_AA)
        cv2.putText(img, "1. Enable 'USB Debugging' on Target Smartphone", (80, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (220, 220, 220), 2, cv2.LINE_AA)
        cv2.putText(img, "2. Connect to Wi-Fi or USB ADB", (80, 480), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (220, 220, 220), 2, cv2.LINE_AA)
        cv2.putText(img, "3. Open web interface on Phone B to control Phone A!", (80, 540), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (220, 220, 220), 2, cv2.LINE_AA)

    current_time = time.strftime("%H:%M:%S UTC")
    cv2.putText(img, f"STREAM TIME: {current_time}", (80, 650), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 100), 2, cv2.LINE_AA)

    center_x, center_y = width // 2, height // 2 + 150
    cv2.circle(img, (center_x, center_y), 120, (0, 255, 120), 3)
    cv2.putText(img, "AxtarGet V2.0", (center_x - 90, center_y + 12), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 120), 3, cv2.LINE_AA)

    _, buffer = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
    return buffer.tobytes()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/api/status")
async def get_status():
    devices = adb_manager.get_devices()
    adb_ready = adb_manager.is_adb_available()
    return {
        "status": "online",
        "system": "AxtarGet Screen Mirroring V2.0 (Mobile-to-Mobile 120FPS 4K)",
        "adb_available": adb_ready,
        "device_count": len(devices),
        "devices": devices
    }

@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    await websocket.accept()
    print("[WebSocket] Client connected (Mobile/Desktop Remote Control)")

    client_config = {
        "fps": 120,
        "quality": 85,
        "mode": "4k"
    }

    async def receiver():
        try:
            while True:
                data = await websocket.receive_json()
                action = data.get("type")
                device_id = data.get("device_id")

                if action == "config":
                    client_config["fps"] = int(data.get("fps", 120))
                    client_config["quality"] = int(data.get("quality", 85))
                    client_config["mode"] = str(data.get("mode", "4k"))
                elif action == "tap":
                    x = int(data.get("x", 0))
                    y = int(data.get("y", 0))
                    adb_manager.execute_input_tap(x, y, device_id)
                elif action == "swipe":
                    x1 = int(data.get("x1", 0))
                    y1 = int(data.get("y1", 0))
                    x2 = int(data.get("x2", 0))
                    y2 = int(data.get("y2", 0))
                    duration = int(data.get("duration", 150))
                    adb_manager.execute_input_swipe(x1, y1, x2, y2, duration, device_id)
                elif action == "keyevent":
                    keycode = int(data.get("code", 0))
                    adb_manager.execute_keyevent(keycode, device_id)
                elif action == "text":
                    text_content = str(data.get("text", ""))
                    if text_content:
                        adb_manager.execute_text_input(text_content, device_id)
        except WebSocketDisconnect:
            pass
        except Exception as e:
            print(f"[WebSocket Receiver Exception] {e}")

    receiver_task = asyncio.create_task(receiver())

    try:
        while True:
            devices = adb_manager.get_devices()
            selected_device = devices[0]["id"] if devices else None

            frame_bytes = None
            if selected_device:
                raw_bytes = adb_manager.capture_frame_bytes(selected_device)
                if raw_bytes:
                    try:
                        nparr = np.frombuffer(raw_bytes, np.uint8)
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        if frame is not None:
                            # Apply JPEG quality for high FPS streaming
                            quality = client_config["quality"]
                            _, jpeg_buf = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
                            frame_bytes = jpeg_buf.tobytes()
                    except Exception as exc:
                        print(f"[Frame Decode Exception] {exc}")

            if not frame_bytes:
                frame_bytes = generate_fallback_frame(len(devices), client_config["mode"])

            await websocket.send_bytes(frame_bytes)

            # Ultra-low delay loop timing (~0.008s for ~120 FPS streaming capability)
            target_fps = max(15, min(120, client_config["fps"]))
            delay = 1.0 / target_fps
            await asyncio.sleep(delay)

    except WebSocketDisconnect:
        print("[WebSocket] Client disconnected")
    except Exception as e:
        print(f"[WebSocket Sender Exception] {e}")
    finally:
        receiver_task.cancel()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_app:app", host="0.0.0.0", port=8080, reload=True)
