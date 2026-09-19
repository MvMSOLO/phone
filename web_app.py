"""
AxtarGet Screen Mirroring V1.4 - Web Application & Screen Streamer
FastAPI & WebSockets powered backend for low-latency Android screen mirroring and remote control.
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
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

app = FastAPI(title="AxtarGet Screen Mirroring V1.4", version="1.4")

# Setup templates directory
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
                    model = "Android Device"
                    for part in parts[2:]:
                        if part.startswith("model:"):
                            model = part.split(":", 1)[1]
                    devices.append({"id": device_id, "model": model, "status": "device"})
            return devices
        except Exception as e:
            print(f"[ADB Error] Failed to list devices: {e}")
            return []

    def capture_frame_bytes(self, device_id: Optional[str] = None) -> Optional[bytes]:
        """Captures screen PNG bytes directly from ADB exec-out screencap -p."""
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

    def execute_input_swipe(self, x1: int, y1: int, x2: int, y2: int, duration_ms: int = 300, device_id: Optional[str] = None):
        cmd = [self.adb_path]
        if device_id:
            cmd.extend(["-s", device_id])
        cmd.extend(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(max(100, duration_ms))])
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
        # Escape spaces for ADB shell input text
        safe_text = text.replace(" ", "%s")
        cmd.extend(["shell", "input", "text", safe_text])
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"[ADB Input Error] Text input failed: {e}")

adb_manager = ADBManager()

def generate_fallback_frame(device_count: int) -> bytes:
    """Generates a high quality Matrix-styled fallback image when no device is connected or frame capture pending."""
    width, height = 720, 1280
    img = np.zeros((height, width, 3), dtype=np.uint8)

    # Dark matrix grid pattern background
    for y in range(0, height, 40):
        cv2.line(img, (0, y), (width, y), (0, 25, 0), 1)
    for x in range(0, width, 40):
        cv2.line(img, (x, 0), (x, height), (0, 25, 0), 1)

    # Outer border
    cv2.rectangle(img, (20, 20), (width - 20, height - 20), (0, 255, 100), 2)

    # Title Text
    cv2.putText(img, "AXTARGET SCREEN MIRRORING V1.4", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 120), 2, cv2.LINE_AA)

    # Status details
    if device_count > 0:
        cv2.putText(img, "STATUS: Device Connected - Stream Initializing...", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 1, cv2.LINE_AA)
    else:
        cv2.putText(img, "STATUS: Waiting for ADB Device...", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 150, 255), 1, cv2.LINE_AA)
        cv2.putText(img, "1. Connect smartphone via USB/Wi-Fi", (50, 260), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1, cv2.LINE_AA)
        cv2.putText(img, "2. Enable 'USB Debugging' in Developer Options", (50, 300), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1, cv2.LINE_AA)
        cv2.putText(img, "3. Authorize ADB prompt on phone screen", (50, 340), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1, cv2.LINE_AA)

    # Dynamic clock text
    current_time = time.strftime("%H:%M:%S UTC")
    cv2.putText(img, f"SERVER TIME: {current_time}", (50, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1, cv2.LINE_AA)

    # Simulated android home icon / graphic
    center_x, center_y = width // 2, height // 2 + 100
    cv2.circle(img, (center_x, center_y), 80, (0, 255, 100), 2)
    cv2.putText(img, "AxtarGet", (center_x - 50, center_y + 8), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 100), 2, cv2.LINE_AA)

    # Encode to JPEG
    _, buffer = cv2.imencode('.jpg', img, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
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
        "system": "AxtarGet Screen Mirroring V1.4",
        "adb_available": adb_ready,
        "device_count": len(devices),
        "devices": devices
    }

@app.websocket("/ws/stream")
async def websocket_stream(websocket: WebSocket):
    await websocket.accept()
    print("[WebSocket] Client connected to screen stream")

    async def receiver():
        try:
            while True:
                data = await websocket.receive_json()
                action = data.get("type")
                device_id = data.get("device_id")

                if action == "tap":
                    x = int(data.get("x", 0))
                    y = int(data.get("y", 0))
                    adb_manager.execute_input_tap(x, y, device_id)
                elif action == "swipe":
                    x1 = int(data.get("x1", 0))
                    y1 = int(data.get("y1", 0))
                    x2 = int(data.get("x2", 0))
                    y2 = int(data.get("y2", 0))
                    duration = int(data.get("duration", 300))
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
            print(f"[WebSocket Error] Receiver error: {e}")

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
                        # Convert PNG raw capture to optimized JPEG for web transport
                        nparr = np.frombuffer(raw_bytes, np.uint8)
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        if frame is not None:
                            # Compress to JPEG with 70% quality for optimal frame rate & low latency
                            _, jpeg_buf = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
                            frame_bytes = jpeg_buf.tobytes()
                    except Exception as exc:
                        print(f"[Frame Processing Error] {exc}")

            if not frame_bytes:
                frame_bytes = generate_fallback_frame(len(devices))

            # Send binary image frame over WebSocket
            await websocket.send_bytes(frame_bytes)
            # Control frame rate (~25-30 FPS)
            await asyncio.sleep(0.035)

    except WebSocketDisconnect:
        print("[WebSocket] Client disconnected")
    except Exception as e:
        print(f"[WebSocket Error] Sender error: {e}")
    finally:
        receiver_task.cancel()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("web_app:app", host="0.0.0.0", port=8080, reload=True)
