"""
Chrome Diagnostic Script
Run this to identify exactly why Chrome isn't launching.

Usage:
    python test_chrome.py
"""

import os
import sys
import shutil

print("=" * 60)
print("  Chrome + ChromeDriver Diagnostic Tool")
print("=" * 60)

# --- Step 1: Python & Selenium version ---
print("\n[1] Environment Info")
print(f"    Python: {sys.version}")
try:
    import selenium
    print(f"    Selenium: {selenium.__version__}")
    major = int(selenium.__version__.split('.')[0])
    minor = int(selenium.__version__.split('.')[1])
    if major < 4 or (major == 4 and minor < 6):
        print("    ⚠️  WARNING: Selenium < 4.6 detected.")
        print("       Run: pip install --upgrade selenium")
    else:
        print("    ✅ Selenium version is good (4.6+ has built-in driver manager)")
except ImportError:
    print("    ❌ Selenium NOT installed. Run: pip install selenium")
    sys.exit(1)

# --- Step 2: Chrome installation ---
print("\n[2] Chrome Browser")
chrome_paths = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
]
found_chrome = None
for path in chrome_paths:
    if os.path.exists(path):
        print(f"    ✅ Found: {path}")
        found_chrome = path
        break
if not found_chrome:
    print("    ❌ Chrome NOT found in standard locations!")
    print("       Install Chrome from: https://www.google.com/chrome/")

# --- Step 3: chromedriver in PATH ---
print("\n[3] ChromeDriver in System PATH")
cd_in_path = shutil.which("chromedriver")
if cd_in_path:
    size = os.path.getsize(cd_in_path)
    print(f"    ✅ Found: {cd_in_path} ({size:,} bytes)")
    if size < 1000:
        print("    ⚠️  WARNING: File is too small — likely a wrapper, not real binary!")
else:
    print("    ℹ️  Not in PATH (that's okay, Selenium can manage this)")

# --- Step 4: webdriver-manager cache ---
print("\n[4] webdriver-manager Cache")
wdm_cache = os.path.expanduser("~\\.wdm")
if os.path.exists(wdm_cache):
    print(f"    Found cache at: {wdm_cache}")
    # Look for chromedriver inside cache
    for root, dirs, files in os.walk(wdm_cache):
        for f in files:
            if "chromedriver" in f.lower():
                full = os.path.join(root, f)
                size = os.path.getsize(full)
                status = "✅" if size > 100_000 else "⚠️  CORRUPT (too small)"
                print(f"    {status} {full} ({size:,} bytes)")
else:
    print("    ℹ️  No cache found (will be created on first use)")

# --- Step 5: Attempt browser launch ---
print("\n[5] Browser Launch Test")
from selenium.webdriver.chrome.options import Options

options = Options()
options.add_argument("--headless=new")  # Run hidden for test
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
if found_chrome:
    options.binary_location = found_chrome

# Try Selenium built-in first
print("    Trying Selenium built-in manager...")
try:
    driver = selenium.webdriver.Chrome(options=options)
    print(f"    ✅ SUCCESS! Browser launched.")
    print(f"       Chrome version: {driver.capabilities.get('browserVersion', 'unknown')}")
    print(f"       ChromeDriver version: {driver.capabilities.get('chrome', {}).get('chromedriverVersion', 'unknown')}")
    driver.quit()
    print("\n✅ Your setup is working! Replace whatsapp_sender.py with the fixed version.")
    sys.exit(0)
except Exception as e:
    print(f"    ❌ Failed: {e}")

# Try webdriver-manager
print("\n    Trying webdriver-manager...")
try:
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service

    # Clear cache first
    if os.path.exists(wdm_cache):
        shutil.rmtree(wdm_cache)
        print("    Cleared corrupted cache...")

    path = ChromeDriverManager().install()
    size = os.path.getsize(path) if os.path.exists(path) else 0
    print(f"    Downloaded to: {path} ({size:,} bytes)")

    if size < 1000:
        print("    ❌ Downloaded file is corrupt (too small).")
        print("       This is a known Windows bug with webdriver-manager.")
        print("       → SOLUTION: Download chromedriver manually:")
        print("         1. Go to: https://googlechromelabs.github.io/chrome-for-testing/")
        print("         2. Find your Chrome version (open chrome://version in Chrome)")
        print("         3. Download 'win64' chromedriver zip")
        print("         4. Extract chromedriver.exe to your project root folder")
        sys.exit(1)

    service = Service(executable_path=path)
    driver = selenium.webdriver.Chrome(service=service, options=options)
    print(f"    ✅ SUCCESS via webdriver-manager!")
    driver.quit()
except Exception as e:
    print(f"    ❌ webdriver-manager also failed: {e}")
    print("\n" + "=" * 60)
    print("MANUAL FIX REQUIRED:")
    print("  1. Open Chrome and go to: chrome://version")
    print("  2. Note your Chrome version (e.g., 131.0.6778.205)")
    print("  3. Go to: https://googlechromelabs.github.io/chrome-for-testing/")
    print("  4. Download chromedriver for your version (win64)")
    print("  5. Unzip and place chromedriver.exe in your project root")
    print("  6. Run: pip install --upgrade selenium")
    print("=" * 60)
