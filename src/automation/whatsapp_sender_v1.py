"""
WhatsApp Automation Module
Handles WhatsApp Web automation for sending messages
"""

import time
import random
from typing import Optional, Callable
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from ..utils.logger import Logger
from ..utils.config import Config

logger = Logger.get_logger(__name__)

class WhatsAppSender:
    """Automates WhatsApp message sending via WhatsApp Web"""
    
    def __init__(self):
        """Initialize WhatsApp sender"""
        self.driver: Optional[webdriver.Chrome] = None
        self.is_logged_in = False
        self.wait: Optional[WebDriverWait] = None
    
    def initialize_browser(self) -> bool:
        """
        Initialize Chrome browser and navigate to WhatsApp Web
        
        Returns:
            bool: True if successful
        """
        try:
            logger.info("Initializing Chrome browser for WhatsApp Web")
            
            # Configure Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Use profile to persist login (optional)
            # chrome_options.add_argument("user-data-dir=./User_Data")
            
            # Initialize Chrome driver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.wait = WebDriverWait(self.driver, Config.BROWSER_WAIT_TIMEOUT)
            
            # Navigate to WhatsApp Web
            self.driver.get(Config.WHATSAPP_WEB_URL)
            logger.info("Browser opened. Please scan QR code to login.")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {str(e)}")
            return False
    
    def wait_for_login(self, timeout: int = 120) -> bool:
        """
        Wait for user to scan QR code and login
        
        Args:
            timeout: Maximum seconds to wait for login
            
        Returns:
            bool: True if login successful
        """
        try:
            logger.info("Waiting for user to scan QR code...")
            
            # Wait for the search box to appear (indicates successful login)
            search_box = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')),
            )
            
            self.is_logged_in = True
            logger.info("Login successful!")
            return True
            
        except TimeoutException:
            logger.error("Login timeout. QR code not scanned.")
            return False
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
    
    def send_message(self, phone_number: str, message: str) -> tuple[bool, str]:
        """
        Send a message to a phone number via WhatsApp
        
        Args:
            phone_number: Recipient's phone number (with country code)
            message: Message to send
            
        Returns:
            Tuple of (success: bool, error_message: str)
        """
        try:
            if not self.is_logged_in:
                return False, "Not logged in to WhatsApp"
            
            logger.info(f"Sending message to {phone_number}")
            
            # Navigate to chat using phone number
            url = f"https://web.whatsapp.com/send?phone={phone_number}"
            self.driver.get(url)
            
            # Wait for chat to load
            time.sleep(3)
            
            # Check if number is valid
            try:
                invalid_number = self.driver.find_element(By.XPATH, '//*[contains(text(), "Phone number shared via url is invalid")]')
                if invalid_number:
                    logger.warning(f"Invalid phone number: {phone_number}")
                    return False, "Invalid phone number"
            except NoSuchElementException:
                pass  # Number is valid
            
            # Find message input box
            message_box = self.wait.until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
            )
            
            # Type message
            message_box.click()
            time.sleep(0.5)
            
            # Split message by lines and send (handles multi-line messages)
            lines = message.split('\n')
            for i, line in enumerate(lines):
                message_box.send_keys(line)
                if i < len(lines) - 1:
                    message_box.send_keys(Keys.SHIFT + Keys.ENTER)
            
            time.sleep(0.5)
            
            # Send message
            message_box.send_keys(Keys.ENTER)
            
            # Wait a moment for message to send
            time.sleep(2)
            
            logger.info(f"Message sent successfully to {phone_number}")
            return True, ""
            
        except TimeoutException:
            error = "Timeout waiting for message box"
            logger.error(f"Failed to send message to {phone_number}: {error}")
            return False, error
        except Exception as e:
            error = str(e)
            logger.error(f"Failed to send message to {phone_number}: {error}")
            return False, error
    
    def send_bulk_messages(self, messages_data: list, 
                          status_callback: Optional[Callable] = None) -> dict:
        """
        Send messages to multiple recipients
        
        Args:
            messages_data: List of dicts with 'phone' and 'message' keys
            status_callback: Callback function for status updates
            
        Returns:
            Dictionary with statistics
        """
        try:
            total = len(messages_data)
            sent = 0
            failed = 0
            
            logger.info(f"Starting bulk send for {total} messages")
            
            for idx, data in enumerate(messages_data):
                phone = data.get('phone')
                message = data.get('message')
                name = data.get('name', 'Unknown')
                
                # Send message
                success, error = self.send_message(phone, message)
                
                if success:
                    sent += 1
                    status = "Sent"
                else:
                    failed += 1
                    status = f"Failed: {error}"
                
                # Call status callback
                if status_callback:
                    progress = (idx + 1) / total * 100
                    status_callback(idx, name, phone, status, progress)
                
                # Random delay between messages to avoid blocking
                if idx < total - 1:  # Don't delay after last message
                    delay = random.uniform(Config.MESSAGE_DELAY_MIN, Config.MESSAGE_DELAY_MAX)
                    logger.info(f"Waiting {delay:.1f} seconds before next message...")
                    time.sleep(delay)
            
            logger.info(f"Bulk send completed: {sent} sent, {failed} failed")
            
            return {
                'total': total,
                'sent': sent,
                'failed': failed,
                'success_rate': (sent / total * 100) if total > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Bulk send failed: {str(e)}")
            raise
    
    def close(self):
        """Close browser and cleanup"""
        try:
            if self.driver:
                self.driver.quit()
                logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {str(e)}")
    
    def is_browser_open(self) -> bool:
        """Check if browser is still open"""
        try:
            if self.driver:
                _ = self.driver.current_url
                return True
            return False
        except:
            return False