"""
Excel file handling module
Manages reading, parsing, and processing Excel files
"""

import pandas as pd
from typing import List, Optional, Dict
from pathlib import Path
from ..utils.logger import Logger
from .validator import DataValidator

logger = Logger.get_logger(__name__)

class ExcelHandler:
    """Handles Excel file operations"""
    
    def __init__(self):
        self.file_path: Optional[str] = None
        self.dataframe: Optional[pd.DataFrame] = None
        self.columns: List[str] = []
    
    def load_file(self, file_path: str) -> bool:
        """
        Load Excel file into memory
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate file first
            is_valid, error_msg = DataValidator.validate_excel_file(file_path)
            if not is_valid:
                logger.error(f"File validation failed: {error_msg}")
                raise ValueError(error_msg)
            
            # Read Excel file
            logger.info(f"Loading Excel file: {file_path}")
            self.dataframe = pd.read_excel(file_path)
            self.file_path = file_path
            self.columns = list(self.dataframe.columns)
            
            logger.info(f"Excel file loaded successfully: {len(self.dataframe)} rows, {len(self.columns)} columns")
            logger.debug(f"Columns: {self.columns}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load Excel file: {str(e)}")
            self.dataframe = None
            self.file_path = None
            self.columns = []
            raise
    
    def get_columns(self) -> List[str]:
        """
        Get list of column names from loaded Excel file
        
        Returns:
            List of column names
        """
        return self.columns
    
    def get_preview_data(self, rows: int = 5) -> pd.DataFrame:
        """
        Get preview of Excel data
        
        Args:
            rows: Number of rows to preview
            
        Returns:
            DataFrame with preview data
        """
        if self.dataframe is None:
            return pd.DataFrame()
        return self.dataframe.head(rows)
    
    def get_processed_data(self, name_col: str, message_col: Optional[str] = None, 
                          phone_col: Optional[str] = None) -> pd.DataFrame:
        """
        Get processed and cleaned data ready for message generation
        
        Args:
            name_col: Name column identifier
            message_col: Message column identifier (optional)
            phone_col: Phone column identifier (optional)
            
        Returns:
            Cleaned DataFrame
        """
        try:
            if self.dataframe is None:
                raise ValueError("No Excel file loaded")
            
            # Validate DataFrame
            is_valid, error_msg = DataValidator.validate_dataframe(
                self.dataframe, name_col, message_col
            )
            if not is_valid:
                raise ValueError(error_msg)
            
            # Clean DataFrame
            cleaned_df = DataValidator.clean_dataframe(
                self.dataframe, name_col, phone_col, message_col
            )
            
            logger.info(f"Processed {len(cleaned_df)} valid contacts")
            return cleaned_df
            
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            raise
    
    def get_row_count(self) -> int:
        """Get total number of rows in loaded Excel file"""
        return len(self.dataframe) if self.dataframe is not None else 0
    
    def export_results(self, df: pd.DataFrame, output_path: str) -> bool:
        """
        Export processed results to Excel file
        
        Args:
            df: DataFrame to export
            output_path: Output file path
            
        Returns:
            bool: True if successful
        """
        try:
            df.to_excel(output_path, index=False)
            logger.info(f"Results exported to: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to export results: {str(e)}")
            return False
    
    def get_column_sample_data(self, column_name: str, rows: int = 3) -> List[str]:
        """
        Get sample data from a specific column for preview
        
        Args:
            column_name: Name of the column
            rows: Number of sample rows
            
        Returns:
            List of sample values
        """
        if self.dataframe is None or column_name not in self.columns:
            return []
        
        sample = self.dataframe[column_name].dropna().head(rows).tolist()
        return [str(val)[:50] for val in sample]  # Truncate long values

    def export_delivery_report(self, delivery_data: List[Dict], output_path: str) -> bool:
        """
        Export delivery report to Excel with formatted columns.
        
        Args:
            delivery_data: List of dicts with keys:
                - name: Contact name
                - phone: Phone number
                - message: Message that was sent
                - status: Delivery status (Sent/Failed)
                - timestamp: When the message was sent
                - error: Error message if failed (optional)
            output_path: Path where report should be saved
            
        Returns:
            bool: True if export successful
        """
        try:
            # Create DataFrame from delivery data
            report_df = pd.DataFrame(delivery_data)
            
            # Reorder columns for better readability
            column_order = ['name', 'phone', 'status', 'timestamp', 'message', 'error']
            existing_cols = [col for col in column_order if col in report_df.columns]
            report_df = report_df[existing_cols]
            
            # Rename columns to be more professional
            report_df.columns = [col.replace('_', ' ').title() for col in report_df.columns]
            
            # Export to Excel with formatting
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                report_df.to_excel(writer, sheet_name='Delivery Report', index=False)
                
                # Get the worksheet to apply formatting
                worksheet = writer.sheets['Delivery Report']
                
                # Auto-adjust column widths
                for idx, col in enumerate(report_df.columns, 1):
                    max_length = max(
                        report_df[col].astype(str).apply(len).max(),
                        len(col)
                    )
                    # Set width with some padding (max 50 chars for message column)
                    adjusted_width = min(max_length + 2, 50 if col == 'Message' else max_length + 2)
                    worksheet.column_dimensions[chr(64 + idx)].width = adjusted_width
            
            logger.info(f"Delivery report exported successfully: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export delivery report: {str(e)}")
            return False