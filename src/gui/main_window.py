"""
Main GUI Window
Implements the primary application interface
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import logging
import pandas as pd
from datetime import datetime
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


class GUILogHandler(logging.Handler):
    """
    Custom logging handler that routes all logger.info() / logger.error() etc.
    calls into the GUI status_text widget in real time.
    
    This means every log message from every module (whatsapp_sender, ai_generator,
    excel_handler etc.) will appear in the GUI — exactly like CMD output.
    """

    # Map logging levels to status tag names used in log_status()
    LEVEL_TAG_MAP = {
        logging.DEBUG:    "DEBUG",
        logging.INFO:     "INFO",
        logging.WARNING:  "WARNING",
        logging.ERROR:    "ERROR",
        logging.CRITICAL: "ERROR",
    }

    def __init__(self, text_widget: scrolledtext.ScrolledText, root: tk.Tk):
        super().__init__()
        self.text_widget = text_widget
        self.root = root
        # Format: "HH:MM:SS | module_name | message"
        self.setFormatter(logging.Formatter("%(asctime)s | %(name)s | %(message)s",
                                            datefmt="%H:%M:%S"))

    def emit(self, record: logging.LogRecord):
        """Called automatically for every log record in the application."""
        try:
            msg = self.format(record)
            level_tag = self.LEVEL_TAG_MAP.get(record.levelno, "INFO")
            # Must update GUI from main thread — use root.after() for thread safety
            self.root.after(0, self._append_to_widget, msg, level_tag)
        except Exception:
            self.handleError(record)

    def _append_to_widget(self, msg: str, tag: str):
        """Append a log line to the text widget (runs on main thread)."""
        try:
            self.text_widget.configure(state=tk.NORMAL)
            self.text_widget.insert(tk.END, msg + "\n", tag)
            self.text_widget.see(tk.END)          # Auto-scroll to bottom
            self.text_widget.configure(state=tk.DISABLED)
        except tk.TclError:
            pass  # Widget may have been destroyed


class MainWindow:
    """Main application window"""
    
    def __init__(self, root):
        """Initialize main window"""
        self.root = root
        self.root.title(f"{Config.APP_NAME} v{Config.APP_VERSION}")
        self.root.geometry(f"{Config.WINDOW_WIDTH}x900")  # Tall enough to show log panel
        self.root.configure(bg=Colors.BACKGROUND)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
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
        self.skip_ai = tk.BooleanVar(value=False)  # New: skip AI checkbox state
        
        # Track successfully sent numbers to avoid duplicates on retry
        self.sent_successfully = set()
        
        # Setup UI
        self.setup_ui()
        
        logger.info("Main window initialized")
    
    def setup_ui(self):
        """Setup the user interface with a scrollable main canvas"""

        # ── Outer container fills the whole window ──────────────────────────
        outer = tk.Frame(self.root, bg=Colors.BACKGROUND)
        outer.pack(fill=tk.BOTH, expand=True)

        # ── Vertical scrollbar on the right ─────────────────────────────────
        v_scroll = tk.Scrollbar(outer, orient=tk.VERTICAL)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # ── Canvas is what actually scrolls ─────────────────────────────────
        self._canvas = tk.Canvas(
            outer,
            bg=Colors.BACKGROUND,
            yscrollcommand=v_scroll.set,
            highlightthickness=0
        )
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.config(command=self._canvas.yview)

        # ── Inner frame lives inside the canvas ─────────────────────────────
        main_frame = tk.Frame(self._canvas, bg=Colors.BACKGROUND)
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=main_frame, anchor="nw"
        )

        # Resize canvas scroll region when inner frame changes size
        def _on_frame_configure(event):
            self._canvas.configure(scrollregion=self._canvas.bbox("all"))

        # Stretch inner frame to canvas width when window is resized
        def _on_canvas_configure(event):
            self._canvas.itemconfig(self._canvas_window, width=event.width)

        main_frame.bind("<Configure>", _on_frame_configure)
        self._canvas.bind("<Configure>", _on_canvas_configure)

        # Mouse wheel scrolling (Windows)
        def _on_mousewheel(event):
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        self._canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # ── Build all sections inside inner padded frame ─────────────────────
        inner = tk.Frame(main_frame, bg=Colors.BACKGROUND)
        inner.pack(fill=tk.BOTH, expand=True, padx=Padding.LARGE, pady=Padding.LARGE)

        # Title
        tk.Label(
            inner,
            text=Config.APP_NAME,
            font=Fonts.TITLE,
            bg=Colors.BACKGROUND,
            fg=Colors.PRIMARY
        ).pack(pady=(0, Padding.LARGE))

        self.create_file_upload_section(inner)
        self.create_column_selection_section(inner)
        self.create_ai_configuration_section(inner)
        self.create_action_buttons(inner)
        self.create_status_section(inner)
    
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

        # Skip AI checkbox
        self.skip_ai_checkbox = tk.Checkbutton(
            content,
            text="⚡ Send messages as-is (skip AI processing)",
            variable=self.skip_ai,
            command=self._on_skip_ai_toggle,
            font=Fonts.NORMAL,
            bg=Colors.SURFACE,
            activebackground=Colors.SURFACE,
            cursor="hand2"
        )
        self.skip_ai_checkbox.pack(anchor=tk.W, pady=(Padding.MEDIUM, Padding.SMALL))
        
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
        
        # Reset Progress Button
        self.reset_btn = tk.Button(
            frame,
            text="Reset Progress",
            command=self.reset_sent_cache,
            font=Fonts.HEADING,
            bg=Colors.WARNING,
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=Padding.XLARGE,
            pady=Padding.MEDIUM,
            state=tk.DISABLED
        )
        self.reset_btn.pack(side=tk.LEFT, padx=Padding.SMALL)
    
    def create_status_section(self, parent):
        """Create live log panel — mirrors CMD output in real time"""
        frame = self.create_section_frame(parent, "📋 Live Logs")

        # ── Toolbar row: label + Clear button ──────────────────────────────
        toolbar = tk.Frame(frame, bg=Colors.SURFACE)
        toolbar.pack(fill=tk.X, padx=Padding.MEDIUM, pady=(Padding.SMALL, 0))

        self.log_count_label = tk.Label(
            toolbar,
            text="Ready",
            font=Fonts.SMALL,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY
        )
        self.log_count_label.pack(side=tk.LEFT)

        clear_btn = tk.Button(
            toolbar,
            text="Clear Logs",
            command=self._clear_logs,
            font=Fonts.SMALL,
            bg=Colors.SURFACE,
            fg=Colors.TEXT_SECONDARY,
            relief=tk.FLAT,
            cursor="hand2",
            bd=1
        )
        clear_btn.pack(side=tk.RIGHT)
        
        # ADDING THE PROGRESS BAR HERE
        self.progress_bar = ttk.Progressbar(
            frame, 
            orient=tk.HORIZONTAL, 
            mode='determinate', 
            length=100
        )
        self.progress_bar.pack(fill=tk.X, padx=Padding.MEDIUM, pady=(Padding.SMALL, Padding.SMALL))

        # ── Dark terminal-style log widget ──────────────────────────────────
        self.status_text = scrolledtext.ScrolledText(
            frame,
            height=12,                  # Taller than before
            font=("Consolas", 9),       # Monospace font like a terminal
            bg="#1e1e1e",               # Dark background
            fg="#d4d4d4",               # Light default text
            insertbackground="white",
            wrap=tk.WORD,
            state=tk.DISABLED,
            relief=tk.FLAT,
            bd=0
        )
        self.status_text.pack(fill=tk.BOTH, expand=True,
                               padx=Padding.MEDIUM, pady=Padding.SMALL)

        # ── Colour tags for different log levels ────────────────────────────
        self.status_text.tag_config("INFO",    foreground="#d4d4d4")   # Light grey
        self.status_text.tag_config("DEBUG",   foreground="#6a9955")   # Green
        self.status_text.tag_config("WARNING", foreground="#dcdcaa")   # Yellow
        self.status_text.tag_config("ERROR",   foreground="#f44747")   # Red
        self.status_text.tag_config("SUCCESS", foreground="#4ec9b0")   # Teal
        self.status_text.tag_config("success", foreground="#4ec9b0")   # Teal (alias)

        # ── Wire up the GUI log handler AFTER widget exists ─────────────────
        self._attach_gui_log_handler()

        # Welcome message
        self._append_log_line("── Log panel ready. All application logs appear here. ──", "DEBUG")
    
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
    
    # ── Logging helpers ────────────────────────────────────────────────────

    def _attach_gui_log_handler(self):
        """
        Attach GUILogHandler to the ROOT Python logger so that every
        logger.info() / logger.error() call in ANY module flows into the GUI.
        """
        self._gui_handler = GUILogHandler(self.status_text, self.root)
        self._gui_handler.setLevel(logging.DEBUG)

        root_logger = logging.getLogger()   # Root logger captures all child loggers
        root_logger.addHandler(self._gui_handler)
        self._log_line_count = 0

    def _append_log_line(self, message: str, tag: str = "INFO"):
        """Directly write a line to the log widget (thread-safe)."""
        self.root.after(0, self._gui_handler._append_to_widget, message, tag)

    def _clear_logs(self):
        """Clear all log entries from the widget."""
        self.status_text.configure(state=tk.NORMAL)
        self.status_text.delete("1.0", tk.END)
        self.status_text.configure(state=tk.DISABLED)
        self.log_count_label.config(text="Logs cleared")

    def log_status(self, message: str, level: str = "INFO"):
        """
        Log a message to the GUI panel.
        Also sends it through the Python logger so it appears in the log file too.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted = f"{timestamp} | GUI | {message}"

        # Write to widget directly
        try:
            self.status_text.configure(state=tk.NORMAL)
            tag = level.lower() if level.lower() in ("error", "warning", "success") else "INFO"
            self.status_text.insert(tk.END, formatted + "\n", tag)
            self.status_text.see(tk.END)
            self.status_text.configure(state=tk.DISABLED)
            self.root.update()
        except tk.TclError:
            pass

        # Also log to file via Python logger
        if level == "ERROR":
            logger.error(message)
        elif level == "WARNING":
            logger.warning(message)
        else:
            logger.info(message)



    def _on_skip_ai_toggle(self):
        """Handle skip AI checkbox toggle"""
        skip = self.skip_ai.get()
        
        # Disable/enable AI-related fields
        if skip:
            self.model_dropdown.config(state='disabled')
            self.prompt_text.config(state=tk.DISABLED, bg='#e0e0e0')
            self.log_status("AI processing disabled - messages will be sent as-is from Excel", "INFO")
        else:
            self.model_dropdown.config(state='readonly')
            self.prompt_text.config(state=tk.NORMAL, bg='white')
            self.log_status("AI processing enabled", "INFO")
    
    def reset_sent_cache(self):
        """Clears the history of successfully sent messages for this session"""
        if not self.sent_successfully:
            self.log_status("Progress is already empty.", "INFO")
            return
            
        if messagebox.askyesno("Confirm Reset", "This will clear the record of messages sent in this session.\n\nThe next 'Send' will include ALL contacts again. Proceed?"):
            count = len(self.sent_successfully)
            self.sent_successfully = set()
            self.log_status(f"Progress reset: {count} contacts cleared from sent cache.", "SUCCESS")
            # Optional: Reset progress bar visual
            self.root.after(0, lambda: self.progress_bar.configure(value=0))

    def _clean_phone_number(self, phone: str, country_code: str = "91") -> str:
        """
        Clean and format phone number for WhatsApp Web.
        - Removes spaces, dashes, brackets, dots
        - Prepends country code if missing
        
        Args:
            phone: Raw phone number string from Excel
            country_code: Default country code to prepend (91 = India)
            
        Returns:
            Cleaned phone number string e.g. "919876543210"
        """
        import re
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', str(phone))
        
        if not digits:
            return ''
        
        # Already has country code (91xxxxxxxxxx = 12 digits for India)
        if digits.startswith('91') and len(digits) == 12:
            return digits
        
        # Has leading 0 (local format like 09876543210)
        if digits.startswith('0'):
            digits = digits[1:]
        
        # Now prepend country code if it's a 10-digit number
        if len(digits) == 10:
            return country_code + digits
        
        # Return as-is if already correct length or unrecognised format
        return digits

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
            skip_ai_mode = self.skip_ai.get()
            
            df = self.excel_handler.get_processed_data(name_col, message_col, phone_col)
            
            # Only initialize AI if not skipping
            if not skip_ai_mode:
                self.log_status(f"Initializing AI model: {self.selected_model.get()}")
                self.ai_generator = AIMessageGenerator(self.selected_model.get())
                self.message_processor = MessageProcessor(self.ai_generator)
            else:
                # Create a dummy processor for skip_ai mode
                self.log_status("Skip AI mode enabled - using messages as-is from Excel")
                # We still need a processor but won't use the AI generator
                if not hasattr(self, 'message_processor') or self.message_processor is None:
                    # Create a minimal processor - AI won't be called
                    self.ai_generator = None
                    self.message_processor = MessageProcessor(None)
            
            # Get custom prompt (ignored if skip_ai is True)
            custom_prompt = self.prompt_text.get('1.0', tk.END).strip()
            
            # Validate message column is selected when skip_ai is True
            if skip_ai_mode and not message_col:
                self.log_status("ERROR: Message column must be selected when 'Skip AI' is enabled", "ERROR")
                messagebox.showerror(
                    "Missing Message Column",
                    "When 'Skip AI' is enabled, you must select a Message Column in Step 2.\n\n"
                    "The messages from that column will be sent as-is."
                )
                return
            
            # Process messages with progress callback
            def progress_callback(progress, success, failed):
                self.log_status(f"Progress: {progress:.1f}% ({success} success, {failed} failed)")
            
            mode_text = "as-is" if skip_ai_mode else "with AI"
            self.log_status(f"Processing {len(df)} contacts {mode_text}...")
            
            self.processed_df = self.message_processor.process_contacts(
                df, name_col, message_col, phone_col, custom_prompt, progress_callback,
                skip_ai=skip_ai_mode
            )
            
            stats = self.message_processor.get_statistics()
            self.log_status(
                f"Processing complete! Success: {stats['processed']}, Failed: {stats['failed']}, "
                f"Rate: {stats['success_rate']:.1f}%",
                "SUCCESS"
            )
            
            # Enable preview and send buttons
            self.root.after(0, lambda: self.preview_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.send_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.reset_btn.config(state=tk.NORMAL))
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
        """
        Thread function for sending messages with duplicate prevention.
        Handles browser initialization, login, bulk sending, and report generation.
        """
        try:
            # Initialize WhatsApp sender if not already open
            if not self.whatsapp_sender or not self.whatsapp_sender.is_browser_open():
                self.whatsapp_sender = WhatsAppSender()
                if not self.whatsapp_sender.initialize_browser():
                    self.log_status("Failed to initialize browser", "ERROR")
                    return
            
            self.log_status("Checking WhatsApp login status...")
            if not self.whatsapp_sender.wait_for_login(timeout=120):
                self.log_status("Login timeout or failed", "ERROR")
                return
            
            self.log_status("Login successful! Preparing message queue...", "SUCCESS")
            
            # Reset visual progress bar
            self.root.after(0, lambda: self.progress_bar.configure(value=0))
            
            phone_col = self.selected_phone_col.get()
            if phone_col == "None" or phone_col not in self.processed_df.columns:
                self.log_status("Phone column not selected or invalid", "ERROR")
                messagebox.showerror("Error", "Please select a valid phone column")
                return

            messages_to_send = []
            # Filter logic: Only add contacts not in the 'sent_successfully' set
            for _, row in self.processed_df.iterrows():
                raw_phone = str(row.get('phone_cleaned', row[phone_col]) or '').strip()
                cleaned_phone = self._clean_phone_number(raw_phone)
                
                if cleaned_phone in self.sent_successfully:
                    continue  # SKIP already sent successfully in this session
                
                messages_to_send.append({
                    'name': row[self.selected_name_col.get()],
                    'phone': cleaned_phone,
                    'message': row['generated_message']
                })

            if not messages_to_send:
                self.log_status("All messages in this list have already been sent successfully.", "SUCCESS")
                messagebox.showinfo("Done", "No pending messages to send.")
                return

            # Status callback for UI updates
            def status_callback(idx, name, phone, status, progress):
                # If sent successfully, add to local session memory
                if status == "Sent":
                    self.sent_successfully.add(phone)
                
                # Update text logs and progress bar
                self.log_status(f"[{idx+1}/{len(messages_to_send)}] {name} ({phone}): {status}")
                self.root.after(0, lambda p=progress: self.progress_bar.configure(value=p))
            
            # Start sending
            stats = self.whatsapp_sender.send_bulk_messages(messages_to_send, status_callback)
            
            self.log_status(
                f"Sending complete! Sent: {stats['sent']}, Failed: {stats['failed']}, "
                f"Rate: {stats['success_rate']:.1f}%",
                "SUCCESS"
            )
            
            # Ensure bar is full at completion
            self.root.after(0, lambda: self.progress_bar.configure(value=100))
            
            # Generate delivery report and get the path
            self._generate_delivery_report(stats)
            
            # Show original detailed popup with success rate and path
            messagebox.showinfo("Complete", 
                f"Sending complete!\n\n"
                f"✅ Sent: {stats['sent']}\n"
                f"❌ Failed: {stats['failed']}\n"
                f"📈 Success Rate: {stats['success_rate']:.1f}%\n\n"
                f"📊 Delivery report saved to:\ndelivery_reports/ folder")
            
        except Exception as e:
            self.log_status(f"Process interrupted: {str(e)}", "ERROR")
            logger.exception("Message sending failed")
        finally:
            # ORIGINAL LOGIC: Close browser and reset button
            if self.whatsapp_sender:
                self.whatsapp_sender.close()
            self.root.after(0, lambda: self.send_btn.config(state=tk.NORMAL))
    
    def _generate_delivery_report(self, stats: dict):
        """
        Generate and save delivery report after sending completes.
        
        Args:
            stats: Statistics dict from send_bulk_messages including delivery_log
        """
        try:
            from datetime import datetime
            from pathlib import Path
            
            # Check if we have delivery data
            if 'delivery_log' not in stats or not stats['delivery_log']:
                self.log_status("No delivery data available for report", "WARNING")
                return
            
            # Create delivery_reports folder if it doesn't exist
            reports_dir = Path(Config.BASE_DIR) / "delivery_reports"
            reports_dir.mkdir(exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_filename = f"delivery_report_{timestamp}.xlsx"
            report_path = reports_dir / report_filename
            
            # Export the report
            self.log_status(f"Generating delivery report: {report_filename}")
            success = self.excel_handler.export_delivery_report(
                stats['delivery_log'],
                str(report_path)
            )
            
            if success:
                self.log_status(f"✅ Delivery report saved: {report_path}", "SUCCESS")
            else:
                self.log_status("Failed to generate delivery report", "ERROR")
                
        except Exception as e:
            self.log_status(f"Error generating delivery report: {str(e)}", "ERROR")
            logger.exception("Delivery report generation failed")
    
    def on_closing(self):
        """Handle window closing with proactive cleanup to prevent hanging"""
        try:
            # Check if sender exists and browser is actually active
            if hasattr(self, 'whatsapp_sender') and self.whatsapp_sender and self.whatsapp_sender.is_browser_open():
                # Prompt the user
                if messagebox.askyesno("Confirm Exit", "WhatsApp automation is active. Close browser and exit?"):
                    # Log the cleanup attempt
                    print("Cleaning up resources before exit...")
                    
                    # Force the browser to quit
                    self.whatsapp_sender.close()
                    
                    # Destroy the GUI window
                    self.root.destroy()
            else:
                # No browser open, just close the window
                self.root.destroy()
        except Exception as e:
            # If anything goes wrong during cleanup, force close anyway
            print(f"Force closing due to error: {e}")
            self.root.destroy()