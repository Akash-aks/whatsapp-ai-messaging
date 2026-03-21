"""
Data validation module
Validates Excel data, phone numbers, and user inputs
"""

import re
import pandas as pd
from typing import Tuple, List
from ..utils.logger import Logger
from ..utils.config import Config

logger = Logger.get_logger(__name__)

class DataValidator:
    """Validates data before processing"""
    
    @staticmethod
    def validate_excel_file(file_path: str) -> Tuple[bool, str]:
        """
        Validate Excel file exists and is readable
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            from pathlib import Path
            path = Path(file_path)
            
            # Check file exists
            if not path.exists():
                return False, "File does not exist"
            
            # Check file extension
            if path.suffix.lower() not in Config.SUPPORTED_EXCEL_FORMATS:
                return False, f"Unsupported file format. Use {', '.join(Config.SUPPORTED_EXCEL_FORMATS)}"
            
            # Try to read the file
            df = pd.read_excel(file_path, nrows=1)
            if df.empty:
                return False, "Excel file is empty"
            
            logger.info(f"Excel file validated successfully: {file_path}")
            return True, ""
            
        except Exception as e:
            logger.error(f"Excel validation failed: {str(e)}")
            return False, f"Error reading Excel file: {str(e)}"
    
    @staticmethod
    def validate_dataframe(df: pd.DataFrame, name_col: str, message_col: str = None) -> Tuple[bool, str]:
        """
        Validate DataFrame has required columns and data
        
        Args:
            df: Pandas DataFrame
            name_col: Name column identifier
            message_col: Message column identifier (optional)
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if DataFrame is empty
            if df.empty:
                return False, "Excel file contains no data"
            
            # Check if name column exists
            if name_col not in df.columns:
                return False, f"Column '{name_col}' not found in Excel file"
            
            # Check if message column exists (if specified)
            if message_col and message_col not in df.columns:
                return False, f"Column '{message_col}' not found in Excel file"
            
            # Check for empty name values
            empty_names = df[name_col].isna().sum()
            if empty_names > 0:
                logger.warning(f"Found {empty_names} empty name values")
            
            # Check contact limit
            if len(df) > Config.MAX_CONTACTS:
                return False, f"Too many contacts ({len(df)}). Maximum allowed: {Config.MAX_CONTACTS}"
            
            logger.info(f"DataFrame validated: {len(df)} contacts")
            return True, ""
            
        except Exception as e:
            logger.error(f"DataFrame validation failed: {str(e)}")
            return False, f"Validation error: {str(e)}"
    
    @staticmethod
    def validate_phone_number(phone: str) -> Tuple[bool, str]:
        """
        Validate phone number format
        
        Args:
            phone: Phone number string
            
        Returns:
            Tuple of (is_valid, cleaned_phone_number)
        """
        try:
            if pd.isna(phone):
                return False, ""
            
            # Convert to string and remove all non-digit characters
            phone_str = str(phone).strip()
            cleaned = re.sub(r'\D', '', phone_str)
            
            # Check if it has at least 10 digits
            if len(cleaned) < 10:
                return False, ""
            
            # Add country code if missing (assuming India +91 by default)
            if not cleaned.startswith('91') and len(cleaned) == 10:
                cleaned = '91' + cleaned
            
            return True, cleaned
            
        except Exception as e:
            logger.error(f"Phone validation error: {str(e)}")
            return False, ""
    
    @staticmethod
    def validate_ai_prompt(prompt: str) -> Tuple[bool, str]:
        """
        Validate AI prompt
        
        Args:
            prompt: AI prompt string
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not prompt or not prompt.strip():
            return False, "AI prompt cannot be empty"
        
        if len(prompt) < 10:
            return False, "AI prompt is too short (minimum 10 characters)"
        
        if len(prompt) > 2000:
            return False, "AI prompt is too long (maximum 2000 characters)"
        
        return True, ""
    
    @staticmethod
    def clean_dataframe(df: pd.DataFrame, name_col: str, phone_col: str = None, message_col: str = None) -> pd.DataFrame:
        """
        Clean and prepare DataFrame for processing
        
        Args:
            df: Input DataFrame
            name_col: Name column
            phone_col: Phone column (optional)
            message_col: Message column (optional)
            
        Returns:
            Cleaned DataFrame
        """
        # Create a copy to avoid modifying original
        df_clean = df.copy()
        
        # Remove rows with empty names
        df_clean = df_clean[df_clean[name_col].notna()]
        
        # Strip whitespace from name column
        df_clean[name_col] = df_clean[name_col].astype(str).str.strip()
        
        # Clean phone numbers if phone column exists
        if phone_col and phone_col in df_clean.columns:
            df_clean['phone_valid'] = df_clean[phone_col].apply(
                lambda x: DataValidator.validate_phone_number(x)[0]
            )
            df_clean['phone_cleaned'] = df_clean[phone_col].apply(
                lambda x: DataValidator.validate_phone_number(x)[1]
            )
        
        # Clean message column if it exists
        if message_col and message_col in df_clean.columns:
            df_clean = df_clean[df_clean[message_col].notna()]
            df_clean[message_col] = df_clean[message_col].astype(str).str.strip()
        
        logger.info(f"DataFrame cleaned: {len(df_clean)} valid contacts")
        return df_clean

