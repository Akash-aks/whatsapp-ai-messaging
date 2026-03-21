"""
Main GUI Window
Implements the primary application interface
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import pandas as pd
from typing import Optional

from .styles import Colors, Fonts, Padding
from .preview_window import PreviewWindow
from ..core.excel_handler import ExcelHandler
from ..core.ai_generator import AIMessageGenerator
from ..core.message_processor import MessageProcessor
from ..automation.whatsapp_sender import WhatsAppSender
from ..utils.logger import Logger
from ..utils.config import Config

logger = Logger.get_logger(__name__)

class MainWindow:
    """Main application window"""
    
    def __init__(self, root):
        """Initialize main window"""
        self.root = root
        self.root.title(f"{Config.APP_NAME} v{Config.APP_VERSION}")
        self.root.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")
        self.root.configure(bg=Colors.BACKGROUND)
        
        # Initialize components
        self.excel_handler = ExcelHandler()
        self.ai_generator: Optional[AIMessageGenerator] = None
        self.message_processor: Optional[MessageProcessor] = None
        self.whatsapp_sender: Optional[WhatsAppSender] = None
        self.processed_df: Optional[pd.DataFrame] = None
        
        # UI State
        self.selected_name_col = tk.StringVar()
        self.selected_message_col = tk.StringVar(value="None")
        self.selected_phone_col = tk.StringVar(value="None")
        self.selected_model = tk.StringVar(value=Config.get_available_models()[0] if Config.get_available_models() else "Claude Sonnet 4")
        self.file_path = tk.StringVar()
        
        # Setup UI
        self.setup_ui()
        
        logger.info("Main window initialized")
    
    def setup_ui(self):
        """Setup the user interface"""
        # Create main container with scrollbar
        main_frame = tk.Frame(self.root, bg=Colors.BACKGROUND)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=Padding.LARGE, pady=Padding.LARGE)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text=Config.APP_NAME,
            font=Fonts.TITLE,
            bg=Colors.BACKGROUND,
            fg=Colors.PRIMARY
        )
        title_label.pack(pady=(0, Padding.LARGE))
        
        # Step 1: File Upload
        self.create_file_upload_section(main_frame)
        
        # Step 2: Column Selection
        self.create_column_selection_section(main_frame)
        
        # Step 3: AI Configuration
        self.create_ai_configuration_section(main_frame)
        
        # Step 4: Action Buttons
        self.create_action_buttons(main_frame)
        
        # Status Section
        self.create_status_section(main_frame)
    
    def create_file_upload_section(self, parent):
        """Create file upload section"""
        frame = self.create_section_frame(parent, "Step 1: Upload Excel File")
        
        # File selection row
        file_frame = tk.Frame(frame, bg=Colors.SURFACE)
        file_frame.pack(fill=tk.X, padx=Padding.MEDIUM, pady=Padding.SMALL)
        
        self.file_entry = tk.Entry(
            file_frame,
            textvariable=self.file_path,
            font=Fonts.NORMAL,
            state='readonly',
            width=50
        )
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, Padding.SMALL))
        
        browse_btn = tk.Button(
            file_frame,
            text="Browse",
            command=self.browse_file,
            font=Fonts.NORMAL_BOLD,
            bg=Colors.PRIMARY,
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=Padding.LARGE
        )
        browse_btn.pack(side=tk.LEFT)
        
        # File info label
        self.file_info_label = tk.Label(
            frame,
            text="No file selected",
            font=Fonts.SMALL,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY
        )
        self.file_info_label.pack(padx=Padding.MEDIUM, pady=(0, Padding.SMALL))
    
    def create_column_selection_section(self, parent):
        """Create column selection section"""
        frame = self.create_section_frame(parent, "Step 2: Select Columns")
        
        content = tk.Frame(frame, bg=Colors.SURFACE)
        content.pack(fill=tk.X, padx=Padding.MEDIUM, pady=Padding.SMALL)
        
        # Name column
        tk.Label(
            content,
            text="Name Column:",
            font=Fonts.NORMAL_BOLD,
            bg=Colors.SURFACE
        ).grid(row=0, column=0, sticky=tk.W, pady=Padding.SMALL)
        
        self.name_col_dropdown = ttk.Combobox(
            content,
            textvariable=self.selected_name_col,
            state='readonly',
            font=Fonts.NORMAL,
            width=25
        )
        self.name_col_dropdown.grid(row=0, column=1, padx=Padding.MEDIUM, pady=Padding.SMALL)
        
        # Phone column
        tk.Label(
            content,
            text="Phone Column:",
            font=Fonts.NORMAL_BOLD,
            bg=Colors.SURFACE
        ).grid(row=1, column=0, sticky=tk.W, pady=Padding.SMALL)
        
        self.phone_col_dropdown = ttk.Combobox(
            content,
            textvariable=self.selected_phone_col,
            state='readonly',
            font=Fonts.NORMAL,
            width=25
        )
        self.phone_col_dropdown.grid(row=1, column=1, padx=Padding.MEDIUM, pady=Padding.SMALL)
        
        # Message column (optional)
        tk.Label(
            content,
            text="Message Column (Optional):",
            font=Fonts.NORMAL_BOLD,
            bg=Colors.SURFACE
        ).grid(row=2, column=0, sticky=tk.W, pady=Padding.SMALL)
        
        self.message_col_dropdown = ttk.Combobox(
            content,
            textvariable=self.selected_message_col,
            state='readonly',
            font=Fonts.NORMAL,
            width=25
        )
        self.message_col_dropdown.grid(row=2, column=1, padx=Padding.MEDIUM, pady=Padding.SMALL)
    
    def create_ai_configuration_section(self, parent):
        """Create AI configuration section"""
        frame = self.create_section_frame(parent, "Step 3: AI Configuration")
        
        content = tk.Frame(frame, bg=Colors.SURFACE)
        content.pack(fill=tk.BOTH, expand=True, padx=Padding.MEDIUM, pady=Padding.SMALL)
        
        # Model selection
        model_frame = tk.Frame(content, bg=Colors.SURFACE)
        model_frame.pack(fill=tk.X, pady=(0, Padding.MEDIUM))
        
        tk.Label(
            model_frame,
            text="AI Model:",
            font=Fonts.NORMAL_BOLD,
            bg=Colors.SURFACE
        ).pack(side=tk.LEFT)
        
        self.model_dropdown = ttk.Combobox(
            model_frame,
            textvariable=self.selected_model,
            values=Config.get_available_models(),
            state='readonly',
            font=Fonts.NORMAL,
            width=25
        )
        self.model_dropdown.pack(side=tk.LEFT, padx=Padding.MEDIUM)
        
        # Custom prompt
        tk.Label(
            content,
            text="Custom AI Prompt (use {name} for name, {message} for original message):",
            font=Fonts.NORMAL_BOLD,
            bg=Colors.SURFACE
        ).pack(anchor=tk.W)
        
        self.prompt_text = scrolledtext.ScrolledText(
            content,
            height=5,
            font=Fonts.NORMAL,
            wrap=tk.WORD
        )
        self.prompt_text.pack(fill=tk.BOTH, expand=True, pady=Padding.SMALL)
        self.prompt_text.insert('1.0', Config.DEFAULT_AI_PROMPT)
    
    def create_action_buttons(self, parent):
        """Create action buttons section"""
        frame = tk.Frame(parent, bg=Colors.BACKGROUND)
        frame.pack(fill=tk.X, pady=Padding.LARGE)
        
        # Generate Messages Button
        self.generate_btn = tk.Button(
            frame,
            text="Generate Messages",
            command=self.generate_messages,
            font=Fonts.HEADING,
            bg=Colors.PRIMARY,
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=Padding.XLARGE,
            pady=Padding.MEDIUM
        )
        self.generate_btn.pack(side=tk.LEFT, padx=Padding.SMALL)
        
        # Preview Button
        self.preview_btn = tk.Button(
            frame,
            text="Preview Messages",
            command=self.preview_messages,
            font=Fonts.HEADING,
            bg=Colors.INFO,
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=Padding.XLARGE,
            pady=Padding.MEDIUM,
            state=tk.DISABLED
        )
        self.preview_btn.pack(side=tk.LEFT, padx=Padding.SMALL)
        
        # Send Messages Button
        self.send_btn = tk.Button(
            frame,
            text="Send via WhatsApp",
            command=self.send_messages,
            font=Fonts.HEADING,
            bg=Colors.SECONDARY,
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=Padding.XLARGE,
            pady=Padding.MEDIUM,
            state=tk.DISABLED
        )
        self.send_btn.pack(side=tk.LEFT, padx=Padding.SMALL)
    
    def create_status_section(self, parent):
        """Create status display section"""
        frame = self.create_section_frame(parent, "Status & Logs")
        
        self.status_text = scrolledtext.ScrolledText(
            frame,
            height=8,
            font=Fonts.SMALL,
            bg=Colors.SURFACE,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.status_text.pack(fill=tk.BOTH, expand=True, padx=Padding.MEDIUM, pady=Padding.SMALL)
    
    def create_section_frame(self, parent, title):
        """Create a section frame with title"""
        frame = tk.LabelFrame(
            parent,
            text=title,
            font=Fonts.HEADING,
            bg=Colors.SURFACE,
            fg=Colors.PRIMARY,
            relief=tk.RIDGE,
            borderwidth=2
        )
        frame.pack(fill=tk.X, pady=Padding.MEDIUM)
        return frame
    
    def log_status(self, message, level="INFO"):
        """Log message to status text widget"""
        self.status_text.configure(state=tk.NORMAL)
        
        # Color coding
        tag = level.lower()
        if tag not in self.status_text.tag_names():
            if level == "ERROR":
                self.status_text.tag_config(tag, foreground=Colors.ERROR)
            elif level == "SUCCESS":
                self.status_text.tag_config(tag, foreground=Colors.SUCCESS)
            elif level == "WARNING":
                self.status_text.tag_config(tag, foreground=Colors.WARNING)
        
        self.status_text.insert(tk.END, f"[{level}] {message}\n", tag)
        self.status_text.see(tk.END)
        self.status_text.configure(state=tk.DISABLED)
        self.root.update()
    
    def browse_file(self):
        """Handle file browse button click"""
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.log_status(f"Loading file: {file_path}")
                self.excel_handler.load_file(file_path)
                self.file_path.set(file_path)
                
                # Update column dropdowns
                columns = ['None'] + self.excel_handler.get_columns()
                self.name_col_dropdown['values'] = self.excel_handler.get_columns()
                self.phone_col_dropdown['values'] = columns
                self.message_col_dropdown['values'] = columns
                
                # Auto-select first column for name
                if self.excel_handler.get_columns():
                    self.selected_name_col.set(self.excel_handler.get_columns()[0])
                
                row_count = self.excel_handler.get_row_count()
                self.file_info_label.config(
                    text=f"✓ Loaded: {row_count} contacts, {len(self.excel_handler.get_columns())} columns"
                )
                self.log_status(f"File loaded successfully: {row_count} contacts", "SUCCESS")
                
            except Exception as e:
                self.log_status(f"Error loading file: {str(e)}", "ERROR")
                messagebox.showerror("Error", f"Failed to load file:\n{str(e)}")
                

    def generate_messages(self):
        """Generate AI messages for all contacts"""
        try:
            # Validate inputs
            if not self.file_path.get():
                messagebox.showwarning("Warning", "Please select an Excel file first")
                return
            
            if not self.selected_name_col.get():
                messagebox.showwarning("Warning", "Please select a name column")
                return
            
            self.log_status("Starting message generation...")
            self.generate_btn.config(state=tk.DISABLED)
            
            # Run in separate thread to prevent GUI freezing
            thread = threading.Thread(target=self._generate_messages_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            self.log_status(f"Error: {str(e)}", "ERROR")
            self.generate_btn.config(state=tk.NORMAL)
    
    def _generate_messages_thread(self):
        """Thread function for message generation"""
        try:
            # Get processed data
            name_col = self.selected_name_col.get()
            message_col = self.selected_message_col.get() if self.selected_message_col.get() != "None" else None
            phone_col = self.selected_phone_col.get() if self.selected_phone_col.get() != "None" else None
            
            df = self.excel_handler.get_processed_data(name_col, message_col, phone_col)
            
            # Initialize AI generator
            self.log_status(f"Initializing AI model: {self.selected_model.get()}")
            self.ai_generator = AIMessageGenerator(self.selected_model.get())
            self.message_processor = MessageProcessor(self.ai_generator)
            
            # Get custom prompt
            custom_prompt = self.prompt_text.get('1.0', tk.END).strip()
            
            # Process messages with progress callback
            def progress_callback(progress, success, failed):
                self.log_status(f"Progress: {progress:.1f}% ({success} success, {failed} failed)")
            
            self.log_status(f"Generating messages for {len(df)} contacts...")
            self.processed_df = self.message_processor.process_contacts(
                df, name_col, message_col, phone_col, custom_prompt, progress_callback
            )
            
            stats = self.message_processor.get_statistics()
            self.log_status(
                f"Generation complete! Success: {stats['processed']}, Failed: {stats['failed']}, "
                f"Rate: {stats['success_rate']:.1f}%",
                "SUCCESS"
            )
            
            # Enable preview and send buttons
            self.root.after(0, lambda: self.preview_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.send_btn.config(state=tk.NORMAL))
            
        except Exception as e:
            self.log_status(f"Generation failed: {str(e)}", "ERROR")
            logger.exception("Message generation failed")
        finally:
            self.root.after(0, lambda: self.generate_btn.config(state=tk.NORMAL))
    
    def preview_messages(self):
        """Show preview window with generated messages"""
        if self.processed_df is not None:
            PreviewWindow(self.root, self.processed_df)
        else:
            messagebox.showwarning("Warning", "No messages to preview. Generate messages first.")
    
    def send_messages(self):
        """Send messages via WhatsApp"""
        if self.processed_df is None:
            messagebox.showwarning("Warning", "No messages to send. Generate messages first.")
            return
        
        # Confirm sending
        if not messagebox.askyesno("Confirm", 
            f"Send {len(self.processed_df)} messages via WhatsApp?\n\n"
            "Make sure:\n"
            "1. You have a stable internet connection\n"
            "2. Your phone number column contains valid numbers\n"
            "3. You're ready to scan QR code"):
            return
        
        self.log_status("Initializing WhatsApp automation...")
        self.send_btn.config(state=tk.DISABLED)
        
        # Run in separate thread
        thread = threading.Thread(target=self._send_messages_thread)
        thread.daemon = True
        thread.start()
    
    def _send_messages_thread(self):
        """Thread function for sending messages"""
        try:
            # Initialize WhatsApp sender
            self.whatsapp_sender = WhatsAppSender()
            
            if not self.whatsapp_sender.initialize_browser():
                self.log_status("Failed to initialize browser", "ERROR")
                return
            
            self.log_status("Please scan QR code in the opened browser...")
            
            if not self.whatsapp_sender.wait_for_login(timeout=120):
                self.log_status("Login timeout or failed", "ERROR")
                return
            
            self.log_status("Login successful! Starting to send messages...", "SUCCESS")
            
            # Prepare messages data
            phone_col = self.selected_phone_col.get()
            if phone_col == "None" or phone_col not in self.processed_df.columns:
                self.log_status("Phone column not selected or invalid", "ERROR")
                messagebox.showerror("Error", "Please select a valid phone column")
                return
            
            messages_data = []
            for _, row in self.processed_df.iterrows():
                messages_data.append({
                    'name': row[self.selected_name_col.get()],
                    'phone': row.get('phone_cleaned', row[phone_col]),
                    'message': row['generated_message']
                })
            
            # Send messages with callback
            def status_callback(idx, name, phone, status, progress):
                self.log_status(f"[{idx+1}/{len(messages_data)}] {name} ({phone}): {status}")
            
            stats = self.whatsapp_sender.send_bulk_messages(messages_data, status_callback)
            
            self.log_status(
                f"Sending complete! Sent: {stats['sent']}, Failed: {stats['failed']}, "
                f"Rate: {stats['success_rate']:.1f}%",
                "SUCCESS"
            )
            
            messagebox.showinfo("Complete", 
                f"Sending complete!\n\n"
                f"Sent: {stats['sent']}\n"
                f"Failed: {stats['failed']}\n"
                f"Success Rate: {stats['success_rate']:.1f}%")
            
        except Exception as e:
            self.log_status(f"Sending failed: {str(e)}", "ERROR")
            logger.exception("Message sending failed")
        finally:
            if self.whatsapp_sender:
                self.whatsapp_sender.close()
            self.root.after(0, lambda: self.send_btn.config(state=tk.NORMAL))
    
    def on_closing(self):
        """Handle window closing"""
        if self.whatsapp_sender and self.whatsapp_sender.is_browser_open():
            if messagebox.askyesno("Confirm", "WhatsApp browser is still open. Close anyway?"):
                self.whatsapp_sender.close()
                self.root.destroy()
        else:
            self.root.destroy()