"""
Pre-requisites Checker
Checks if system meets all requirements before installation
Run this BEFORE setup.sh or setup.bat
"""

import sys
import subprocess
import platform
import os
from pathlib import Path

def print_header(text):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(text)
    print("="*60)

def print_status(status, message):
    """Print status with icon"""
    icons = {
        "ok": "✅",
        "warning": "⚠️",
        "error": "❌",
        "info": "ℹ️"
    }
    print(f"{icons.get(status, '•')} {message}")

def check_python():
    """Check Python installation and version"""
    print_header("Checking Python")
    
    try:
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        print_status("info", f"Python version: {version_str}")
        
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print_status("error", "Python 3.8 or higher required")
            print_status("info", "Download from: https://www.python.org/downloads/")
            return False
        
        print_status("ok", "Python version is compatible")
        return True
    except Exception as e:
        print_status("error", f"Failed to check Python: {e}")
        return False

def check_pip():
    """Check pip installation"""
    print_header("Checking pip")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print_status("ok", "pip is installed")
            print_status("info", result.stdout.strip())
            return True
        else:
            print_status("error", "pip not found")
            print_status("info", "Install with: python -m ensurepip --upgrade")
            return False
    except Exception as e:
        print_status("error", f"Failed to check pip: {e}")
        return False

def check_venv():
    """Check if venv module is available"""
    print_header("Checking venv module")
    
    try:
        import venv
        print_status("ok", "venv module is available")
        return True
    except ImportError:
        print_status("error", "venv module not found")
        
        os_type = platform.system()
        if os_type == "Linux":
            print_status("info", "Install with: sudo apt-get install python3-venv")
        
        return False

def check_chrome():
    """Check Chrome/Chromium installation"""
    print_header("Checking Chrome/Chromium")
    
    os_type = platform.system()
    
    chrome_paths = {
        "Windows": [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ],
        "Darwin": [  # Mac
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
        ],
        "Linux": [
            "/usr/bin/google-chrome",
            "/usr/bin/chromium-browser",
            "/usr/bin/chromium",
        ]
    }
    
    paths_to_check = chrome_paths.get(os_type, [])
    
    for path in paths_to_check:
        if os.path.exists(path):
            print_status("ok", f"Chrome found: {path}")
            return True
    
    # Also check PATH
    chrome_commands = ["google-chrome", "chromium-browser", "chromium", "chrome"]
    for cmd in chrome_commands:
        try:
            result = subprocess.run(
                ["which" if os_type != "Windows" else "where", cmd],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                print_status("ok", f"Chrome found: {cmd}")
                return True
        except:
            pass
    
    print_status("warning", "Chrome/Chromium not found")
    print_status("info", "Chrome is required for WhatsApp automation")
    
    if os_type == "Windows":
        print_status("info", "Download from: https://www.google.com/chrome/")
    elif os_type == "Darwin":
        print_status("info", "Install with: brew install --cask google-chrome")
    elif os_type == "Linux":
        print_status("info", "Install with: sudo apt-get install chromium-browser")
    
    return False

def check_internet():
    """Check internet connection"""
    print_header("Checking Internet Connection")
    
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        print_status("ok", "Internet connection available")
        return True
    except OSError:
        print_status("warning", "No internet connection")
        print_status("info", "Internet needed for initial setup")
        return False

def check_disk_space():
    """Check available disk space"""
    print_header("Checking Disk Space")
    
    try:
        import shutil
        
        total, used, free = shutil.disk_usage(".")
        
        free_gb = free // (2**30)
        
        print_status("info", f"Free space: {free_gb} GB")
        
        if free_gb < 1:
            print_status("error", "Less than 1GB free space")
            print_status("info", "At least 1GB recommended for dependencies")
            return False
        elif free_gb < 2:
            print_status("warning", "Low disk space (less than 2GB)")
            return True
        else:
            print_status("ok", "Sufficient disk space")
            return True
    except Exception as e:
        print_status("warning", f"Could not check disk space: {e}")
        return True

def check_project_files():
    """Check if required project files exist"""
    print_header("Checking Project Files")
    
    required_files = [
        "requirements.txt",
        "main.py",
        ".env.example",
        "src/utils/config.py",
        "src/core/ai_generator.py"
    ]
    
    all_exist = True
    for file in required_files:
        path = Path(file)
        if path.exists():
            print_status("ok", f"{file}")
        else:
            print_status("error", f"Missing: {file}")
            all_exist = False
    
    if not all_exist:
        print_status("warning", "Some project files are missing")
        print_status("info", "Make sure you have all files from the repository")
    
    return all_exist

def check_permissions():
    """Check write permissions"""
    print_header("Checking Permissions")
    
    try:
        # Try to create a test file
        test_file = Path("test_permissions.tmp")
        test_file.write_text("test")
        test_file.unlink()
        
        print_status("ok", "Write permissions available")
        return True
    except PermissionError:
        print_status("error", "No write permissions in current directory")
        
        os_type = platform.system()
        if os_type == "Linux":
            print_status("info", "Try running with sudo or change directory ownership")
        
        return False
    except Exception as e:
        print_status("warning", f"Permission check failed: {e}")
        return True

def main():
    """Run all checks"""
    print("\n" + "🔍 "*15)
    print("Pre-requisites Checker for WhatsApp AI Automation")
    print("🔍 "*15)
    
    print_status("info", f"Operating System: {platform.system()} {platform.release()}")
    print_status("info", f"Python Executable: {sys.executable}")
    
    checks = {
        "Python 3.8+": check_python(),
        "pip": check_pip(),
        "venv module": check_venv(),
        "Chrome/Chromium": check_chrome(),
        "Internet connection": check_internet(),
        "Disk space": check_disk_space(),
        "Project files": check_project_files(),
        "Write permissions": check_permissions()
    }
    
    print_header("Summary")
    
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    
    for check_name, result in checks.items():
        status = "ok" if result else "error"
        print_status(status, check_name)
    
    print()
    print(f"Passed: {passed}/{total} checks")
    
    if passed == total:
        print_status("ok", "All checks passed! Ready to run setup.")
        print()
        print("Next steps:")
        print("  Windows: setup.bat")
        print("  Linux/Mac: ./setup.sh")
        return True
    else:
        failed = total - passed
        print_status("warning", f"{failed} check(s) failed")
        print()
        print("Please fix the issues above before running setup.")
        
        # Provide OS-specific help
        os_type = platform.system()
        if os_type == "Linux":
            print()
            print("Common fixes for Linux:")
            print("  sudo apt-get install python3 python3-pip python3-venv chromium-browser")
        elif os_type == "Darwin":
            print()
            print("Common fixes for Mac:")
            print("  brew install python3")
            print("  brew install --cask google-chrome")
        
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nCheck interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)