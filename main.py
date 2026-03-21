"""
WhatsApp AI Message Automation
Main Entry Point

A production-ready desktop application for automating personalized WhatsApp messaging using AI.

Author: Engineering Project
Version: 1.0.0
"""

import tkinter as tk
from tkinter import messagebox
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.gui.main_window import MainWindow
from src.utils.logger import Logger
from src.utils.config import Config

def main():
    """Main application entry point"""
    # Initialize logging
    Logger.log_session_start()
    logger = Logger.get_logger(__name__)
    
    try:
        logger.info("Starting WhatsApp AI Automation application...")
        
        # Validate API keys
        issues = Config.validate_api_keys()
        if issues:
            logger.warning("API key validation issues found")
            messagebox.showwarning(
                "Configuration Warning",
                "\n".join(issues) + "\n\nYou won't be able to use AI features without API keys."
            )
        
        # Create root window
        root = tk.Tk()
        
        # Create main application window
        app = MainWindow(root)
        
        # Handle window close
        root.protocol("WM_DELETE_WINDOW", app.on_closing)
        
        # Start the GUI event loop
        logger.info("Application window initialized. Starting event loop...")
        root.mainloop()
        
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}", exc_info=True)
        messagebox.showerror("Fatal Error", f"Application failed to start:\n{str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()