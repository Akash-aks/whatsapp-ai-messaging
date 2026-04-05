"""
WhatsApp Automation Module
Handles WhatsApp Web automation for sending messages

FIXED: [WinError 193] - Now uses Selenium's built-in driver manager
instead of webdriver-manager to avoid corrupted ChromeDriver binaries on Windows.
"""

import time
import random
import os
import shutil
from typing import Optional, Callable
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from ..utils.logger import Logger
from ..utils.config import Config

logger = Logger.get_logger(__name__)


def _find_chrome_binary() -> Optional[str]:
    """
    Find the Chrome browser executable on Windows.
    Returns the path if found, None otherwise.
    """
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES%\Google\Chrome\Application\chrome.exe"),
        os.path.expandvars(r"%PROGRAMFILES(X86)%\Google\Chrome\Application\chrome.exe"),
    ]
    for path in chrome_paths:
        if os.path.exists(path):
            logger.info(f"Chrome found at: {path}")
            return path
    logger.warning("Chrome not found in standard paths. Will let Selenium auto-detect.")
    return None


def _clear_wdm_cache():
    """
    Clear the webdriver-manager cache to remove any corrupted binaries.
    This resolves [WinError 193] caused by bad cached drivers.
    """
    cache_path = os.path.expanduser("~\\.wdm")
    if os.path.exists(cache_path):
        try:
            shutil.rmtree(cache_path)
            logger.info("Cleared webdriver-manager cache.")
        except Exception as e:
            logger.warning(f"Could not clear wdm cache: {e}")


def _build_chrome_options() -> Options:
    """
    Build Chrome options for WhatsApp Web automation.
    Returns configured Options object.
    """
    options = Options()
    
    # Saves login session between runs
    #profile_dir = os.path.join(os.path.expanduser("~"), "whatsapp_chrome_profile")
    #options.add_argument(f"--user-data-dir={profile_dir}")
    # Path to store the WhatsApp session data
    # This creates a folder named 'whatsapp_session' in your project root
    session_path = os.path.join(os.getcwd(), "whatsapp_session")
    options.add_argument(f"--user-data-dir={session_path}")
    options.add_argument("--profile-directory=Default")

    # Anti-detection settings
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    options.add_argument("--log-level=3")  # Fatal errors only
    options.add_argument("--silent") 
    options.exclude_switches = ["enable-logging"] # Specifically hides the DevTools/GCM logs

    # Stability settings
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")

    # Set Chrome binary location if found
    chrome_binary = _find_chrome_binary()
    if chrome_binary:
        options.binary_location = chrome_binary

    return options


class WhatsAppSender:
    """Automates WhatsApp message sending via WhatsApp Web"""

    def __init__(self):
        """Initialize WhatsApp sender"""
        self.driver: Optional[webdriver.Chrome] = None
        self.is_logged_in = False
        self.wait: Optional[WebDriverWait] = None

    def initialize_browser(self) -> bool:
        """
        Initialize Chrome browser and navigate to WhatsApp Web.

        Strategy (in order of attempt):
        1. Selenium's built-in selenium-manager (most reliable, no cache issues)
        2. System chromedriver from PATH
        3. webdriver-manager fallback (after clearing cache)

        Returns:
            bool: True if browser launched successfully
        """
        logger.info("Initializing Chrome browser for WhatsApp Web")
        options = _build_chrome_options()

        # --- Strategy 1: Selenium built-in manager (best for Windows) ---
        try:
            logger.info("Attempting launch via Selenium built-in manager...")
            # Passing no Service lets Selenium 4.6+ use its own selenium-manager
            self.driver = webdriver.Chrome(options=options)
            self.wait = WebDriverWait(self.driver, Config.BROWSER_WAIT_TIMEOUT)
            self.driver.get(Config.WHATSAPP_WEB_URL)
            logger.info("Browser opened successfully via Selenium manager.")
            return True
        except Exception as e1:
            logger.warning(f"Selenium built-in manager failed: {e1}")

        # --- Strategy 2: chromedriver from system PATH ---
        try:
            logger.info("Attempting launch via system PATH chromedriver...")
            chromedriver_in_path = shutil.which("chromedriver")
            if chromedriver_in_path:
                service = Service(executable_path=chromedriver_in_path)
                self.driver = webdriver.Chrome(service=service, options=options)
                self.wait = WebDriverWait(self.driver, Config.BROWSER_WAIT_TIMEOUT)
                self.driver.get(Config.WHATSAPP_WEB_URL)
                logger.info("Browser opened successfully via system PATH.")
                return True
            else:
                logger.warning("chromedriver not found in system PATH.")
        except Exception as e2:
            logger.warning(f"System PATH chromedriver failed: {e2}")

        # --- Strategy 3: webdriver-manager (after clearing bad cache) ---
        try:
            logger.info("Attempting launch via webdriver-manager (clearing cache first)...")
            _clear_wdm_cache()

            from webdriver_manager.chrome import ChromeDriverManager
            driver_path = ChromeDriverManager().install()

            # Validate the downloaded file is a real binary (not a text wrapper)
            if os.path.exists(driver_path):
                file_size = os.path.getsize(driver_path)
                if file_size < 1000:  # Real chromedriver.exe is several MB
                    raise RuntimeError(
                        f"ChromeDriver at '{driver_path}' looks invalid "
                        f"(file size only {file_size} bytes). "
                        "This is a known webdriver-manager issue on Windows."
                    )

            service = Service(executable_path=driver_path)
            self.driver = webdriver.Chrome(service=service, options=options)
            self.wait = WebDriverWait(self.driver, Config.BROWSER_WAIT_TIMEOUT)
            self.driver.get(Config.WHATSAPP_WEB_URL)
            logger.info("Browser opened successfully via webdriver-manager.")
            return True
        except Exception as e3:
            logger.error(f"All browser launch strategies failed. Last error: {e3}")
            logger.error(
                "\n\n=== BROWSER SETUP HELP ===\n"
                "Could not launch Chrome automatically. Please try:\n"
                "1. Update Chrome to the latest version\n"
                "2. Download ChromeDriver manually from:\n"
                "   https://googlechromelabs.github.io/chrome-for-testing/\n"
                "   - Match your Chrome version (check chrome://version)\n"
                "   - Download 'win64' version\n"
                "   - Place chromedriver.exe in your project root folder\n"
                "3. Run: pip install --upgrade selenium webdriver-manager\n"
            )
            return False

    def wait_for_login(self, timeout: int = 120) -> bool:
        """
        Wait for user to scan QR code and login.

        Args:
            timeout: Maximum seconds to wait for login

        Returns:
            bool: True if login successful
        """
        try:
            logger.info("Waiting for user to scan QR code...")

            # Override wait timeout for login (needs more time)
            login_wait = WebDriverWait(self.driver, timeout)
            
            # A more resilient way to detect login
            stable_markers = [
                '//div[@role="textbox"]',      # Search box
                '//div[@id="pane-side"]',      # Chat list
                '//header[@role="banner"]',    # Top profile header
                '//span[@data-icon="chat"]'    # The "New Chat" icon
            ]
            combined_query = " | ".join(stable_markers)

            # Wait for the search box to appear (indicates successful login)
            login_wait.until(
                EC.presence_of_element_located(
                    #(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
                    #(By.XPATH, '//div[@contenteditable="true"][@role="textbox"]')
                    (By.XPATH, combined_query)
                )
            )

            self.is_logged_in = True
            logger.info("Login successful!")
            return True

        except TimeoutException:
            logger.error("Login timeout. QR code not scanned within time limit.")
            return False
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False

    def send_message(self, phone_number: str, message: str, max_retries: int = 2) -> tuple[bool, str]:
        """
        Send a message with an individual retry mechanism.
        """
        attempt = 0
        last_error = ""

        while attempt <= max_retries:
            try:
                if not self.is_logged_in:
                    return False, "Not logged in to WhatsApp"

                # If it's a retry, log it
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt} for {phone_number}...")

                # Navigate to chat
                url = f"https://web.whatsapp.com/send?phone={phone_number}"
                self.driver.get(url)

                # Wait for chat to load (checks for the message box)
                message_box = self.wait.until(
                    EC.presence_of_element_located(
                        (By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
                    )
                )

                # Small delay to ensure focus
                time.sleep(1)
                message_box.click()

                # Handle multi-line messages
                lines = message.split('\n')
                for i, line in enumerate(lines):
                    message_box.send_keys(line)
                    if i < len(lines) - 1:
                        message_box.send_keys(Keys.SHIFT + Keys.ENTER)

                time.sleep(0.5)
                message_box.send_keys(Keys.ENTER)
                
                # Wait to confirm the send action happened
                time.sleep(2)

                logger.info(f"Message sent successfully to {phone_number}")
                return True, ""

            except Exception as e:
                attempt += 1
                last_error = str(e)
                logger.warning(f"Attempt {attempt} failed for {phone_number}: {last_error}")
                
                # Check for invalid number popup specifically
                try:
                    invalid = self.driver.find_elements(By.XPATH, '//*[contains(text(), "invalid")]')
                    if invalid:
                        return False, "Invalid phone number"
                except:
                    pass
                
                time.sleep(3) # Wait before retry

        return False, f"Failed after {max_retries} retries: {last_error}"

    def send_bulk_messages(
        self,
        messages_data: list,
        status_callback: Optional[Callable] = None
    ) -> dict:
        """
        Send messages to multiple recipients with safe delays.

        Args:
            messages_data: List of dicts with 'phone', 'message', and 'name' keys
            status_callback: Optional callback(idx, name, phone, status, progress)

        Returns:
            Dictionary with send statistics and detailed delivery_log
        """
        try:
            from datetime import datetime
            
            total = len(messages_data)
            sent = 0
            failed = 0
            delivery_log = []  # Track detailed delivery info for report

            logger.info(f"Starting bulk send for {total} messages")

            for idx, data in enumerate(messages_data):
                phone = data.get('phone', '').strip()
                message = data.get('message', '')
                name = data.get('name', 'Unknown')
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                if not phone:
                    failed += 1
                    status = "Failed"
                    error_msg = "No phone number"
                    logger.warning(f"Skipping {name} — no phone number provided")
                    
                    # Log delivery record
                    delivery_log.append({
                        'name': name,
                        'phone': phone or 'N/A',
                        'message': message[:100],  # Truncate for report
                        'status': status,
                        'timestamp': timestamp,
                        'error': error_msg
                    })
                else:
                    success, error = self.send_message(phone, message)
                    
                    if success:
                        sent += 1
                        status = "Sent"
                        error_msg = ""
                    else:
                        failed += 1
                        status = "Failed"
                        error_msg = error[:100]  # Truncate long errors
                    
                    # Log delivery record
                    delivery_log.append({
                        'name': name,
                        'phone': phone,
                        'message': message[:100],
                        'status': status,
                        'timestamp': timestamp,
                        'error': error_msg
                    })

                # Update UI status
                if status_callback:
                    progress = (idx + 1) / total * 100
                    status_callback(idx, name, phone, status, progress)

                # Random delay to avoid WhatsApp rate-limiting
                if idx < total - 1:
                    delay = random.uniform(Config.MESSAGE_DELAY_MIN, Config.MESSAGE_DELAY_MAX)
                    logger.info(f"Waiting {delay:.1f}s before next message...")
                    time.sleep(delay)

            result = {
                'total': total,
                'sent': sent,
                'failed': failed,
                'success_rate': (sent / total * 100) if total > 0 else 0,
                'delivery_log': delivery_log  # NEW: detailed delivery data
            }
            logger.info(
                f"Bulk send complete: {sent}/{total} sent "
                f"({result['success_rate']:.1f}% success rate)"
            )
            return result

        except Exception as e:
            logger.error(f"Bulk send failed: {str(e)}")
            raise

    def close(self):
        """Close browser and cleanup resources quickly"""
        try:
            if self.driver:
                # quit() is the heavy-duty command that kills the background process
                self.driver.quit()
                # IMPORTANT: Reset variables so the app knows the browser is gone
                self.driver = None
                self.is_logged_in = False
                logger.info("Browser closed successfully")
        except Exception as e:
            # If the driver is already stuck, we force the variable to None 
            # so the GUI can finish closing
            self.driver = None 
            logger.error(f"Error closing browser: {str(e)}")

    def is_browser_open(self) -> bool:
        """Check if browser is still open and responsive"""
        try:
            if self.driver:
                _ = self.driver.current_url
                return True
            return False
        except Exception:
            return False