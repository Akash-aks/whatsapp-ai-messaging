"""
Preview Window
Shows generated messages in a table format before sending
"""

import tkinter as tk
from tkinter import ttk
import pandas as pd

from .styles import Colors, Fonts, Padding
from ..utils.config import Config

class PreviewWindow:
    """Window for previewing generated messages"""
    
    def __init__(self, parent, dataframe: pd.DataFrame):
        """
        Initialize preview window
        
        Args:
            parent: Parent window
            dataframe: DataFrame with generated messages
        """
        self.df = dataframe
        
        # Create toplevel window
        self.window = tk.Toplevel(parent)
        self.window.title("Message Preview")
        self.window.geometry(f"{Config.PREVIEW_WINDOW_WIDTH}x{Config.PREVIEW_WINDOW_HEIGHT}")
        self.window.configure(bg=Colors.BACKGROUND)
        
        # Make it modal
        self.window.transient(parent)
        self.window.grab_set()
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the preview window UI"""
        # Title
        title_frame = tk.Frame(self.window, bg=Colors.BACKGROUND)
        title_frame.pack(fill=tk.X, padx=Padding.LARGE, pady=Padding.MEDIUM)
        
        title_label = tk.Label(
            title_frame,
            text="Generated Messages Preview",
            font=Fonts.TITLE,
            bg=Colors.BACKGROUND,
            fg=Colors.PRIMARY
        )
        title_label.pack()
        
        # Summary
        summary_text = f"Total Contacts: {len(self.df)}"
        summary_label = tk.Label(
            title_frame,
            text=summary_text,
            font=Fonts.NORMAL,
            bg=Colors.BACKGROUND,
            fg=Colors.TEXT_SECONDARY
        )
        summary_label.pack()
        
        # Create treeview for displaying messages
        tree_frame = tk.Frame(self.window, bg=Colors.BACKGROUND)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=Padding.LARGE, pady=(0, Padding.MEDIUM))
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL)
        
        # Treeview
        columns = ['#', 'Name', 'Generated Message', 'Status']
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        # Configure scrollbars
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
        
        # Define column headings and widths
        self.tree.heading('#', text='#')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Generated Message', text='Generated Message')
        self.tree.heading('Status', text='Status')
        
        self.tree.column('#', width=50, anchor=tk.CENTER)
        self.tree.column('Name', width=150)
        self.tree.column('Generated Message', width=400)
        self.tree.column('Status', width=100, anchor=tk.CENTER)
        
        # Pack widgets
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Populate tree with data
        self.populate_tree()
        
        # Buttons
        button_frame = tk.Frame(self.window, bg=Colors.BACKGROUND)
        button_frame.pack(fill=tk.X, padx=Padding.LARGE, pady=Padding.MEDIUM)
        
        export_btn = tk.Button(
            button_frame,
            text="Export to Excel",
            command=self.export_to_excel,
            font=Fonts.NORMAL_BOLD,
            bg=Colors.PRIMARY,
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=Padding.LARGE,
            pady=Padding.SMALL
        )
        export_btn.pack(side=tk.LEFT, padx=Padding.SMALL)
        
        close_btn = tk.Button(
            button_frame,
            text="Close",
            command=self.window.destroy,
            font=Fonts.NORMAL_BOLD,
            bg=Colors.TEXT_SECONDARY,
            fg="white",
            cursor="hand2",
            relief=tk.FLAT,
            padx=Padding.LARGE,
            pady=Padding.SMALL
        )
        close_btn.pack(side=tk.RIGHT, padx=Padding.SMALL)
    
    def populate_tree(self):
        """Populate treeview with message data"""
        # Get name column (assuming it's the first non-system column)
        name_col = None
        for col in self.df.columns:
            if col not in ['generated_message', 'generation_status', 'phone_valid', 'phone_cleaned']:
                name_col = col
                break
        
        if name_col is None:
            name_col = self.df.columns[0]
        
        # Insert data
        for idx, row in self.df.iterrows():
            name = row[name_col]
            message = row['generated_message']
            status = row['generation_status']
            
            # Truncate long messages for display
            display_message = message[:100] + "..." if len(message) > 100 else message
            
            # Color code by status
            tag = 'success' if status == 'Success' else 'error'
            
            self.tree.insert('', tk.END, values=(idx+1, name, display_message, status), tags=(tag,))
        
        # Configure tags for color coding
        self.tree.tag_configure('success', background='#d4edda')
        self.tree.tag_configure('error', background='#f8d7da')
    
    def export_to_excel(self):
        """Export messages to Excel file"""
        from tkinter import filedialog
        import os
        
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile="generated_messages.xlsx"
        )
        
        if file_path:
            try:
                self.df.to_excel(file_path, index=False)
                tk.messagebox.showinfo("Success", f"Messages exported successfully to:\n{file_path}")
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to export:\n{str(e)}")