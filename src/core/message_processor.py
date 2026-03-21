"""
Message Processing Module
Orchestrates message generation for multiple contacts
"""

import pandas as pd
from typing import Optional, Callable
from .ai_generator import AIMessageGenerator
from ..utils.logger import Logger

logger = Logger.get_logger(__name__)

class MessageProcessor:
    """Processes and generates messages for multiple contacts"""
    
    def __init__(self, ai_generator: Optional[AIMessageGenerator]):
        """
        Initialize message processor
        
        Args:
            ai_generator: AI generator instance (can be None if skip_ai mode is used)
        """
        self.ai_generator = ai_generator
        self.processed_count = 0
        self.failed_count = 0
    
    def process_contacts(self, df: pd.DataFrame, name_col: str, 
                        message_col: Optional[str] = None,
                        phone_col: Optional[str] = None,
                        custom_prompt: Optional[str] = None,
                        progress_callback: Optional[Callable] = None,
                        skip_ai: bool = False) -> pd.DataFrame:
        """
        Process all contacts and generate personalized messages
        
        Args:
            df: DataFrame with contact data
            name_col: Name column identifier
            message_col: Message column identifier (optional)
            phone_col: Phone column identifier (optional)
            custom_prompt: Custom AI prompt (optional)
            progress_callback: Callback function for progress updates (optional)
            skip_ai: If True, use messages from Excel as-is without AI processing
            
        Returns:
            DataFrame with generated messages
        """
        try:
            logger.info(f"Starting message processing for {len(df)} contacts")
            
            # Create result DataFrame
            result_df = df.copy()
            result_df['generated_message'] = ''
            result_df['generation_status'] = 'Pending'
            
            self.processed_count = 0
            self.failed_count = 0
            total = len(df)
            
            # Process each contact
            for idx, row in df.iterrows():
                try:
                    name = row[name_col]
                    original_message = row[message_col] if message_col and message_col in df.columns else None
                    
                    # Generate or use existing message
                    if skip_ai:
                        # Use message from Excel as-is (no AI processing)
                        if original_message and str(original_message).strip():
                            generated_msg = str(original_message).strip()
                            logger.debug(f"Using message as-is for {name}")
                        else:
                            # No message in Excel and skip_ai is enabled
                            generated_msg = f"Hi {name}, this is a message for you."
                            logger.warning(f"No message found for {name}, using default")
                    else:
                        # Use AI to generate/improve message
                        generated_msg = self.ai_generator.generate_message(
                            name=str(name),
                            original_message=str(original_message) if original_message else None,
                            custom_prompt=custom_prompt
                        )
                    
                    result_df.at[idx, 'generated_message'] = generated_msg
                    result_df.at[idx, 'generation_status'] = 'Success'
                    self.processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to generate message for {name}: {str(e)}")
                    result_df.at[idx, 'generation_status'] = f'Failed: {str(e)[:50]}'
                    self.failed_count += 1
                
                # Call progress callback if provided
                if progress_callback:
                    progress = (self.processed_count + self.failed_count) / total * 100
                    progress_callback(progress, self.processed_count, self.failed_count)
            
            logger.info(f"Message processing completed: {self.processed_count} success, {self.failed_count} failed")
            return result_df
            
        except Exception as e:
            logger.error(f"Message processing failed: {str(e)}")
            raise
    
    def generate_single_message(self, name: str, original_message: Optional[str] = None,
                               custom_prompt: Optional[str] = None) -> str:
        """
        Generate a single message (useful for testing)
        
        Args:
            name: Recipient name
            original_message: Original message to improve
            custom_prompt: Custom prompt
            
        Returns:
            Generated message
        """
        return self.ai_generator.generate_message(name, original_message, custom_prompt)
    
    def get_statistics(self) -> dict:
        """
        Get processing statistics
        
        Returns:
            Dictionary with processing stats
        """
        return {
            'processed': self.processed_count,
            'failed': self.failed_count,
            'total': self.processed_count + self.failed_count,
            'success_rate': (self.processed_count / (self.processed_count + self.failed_count) * 100) 
                           if (self.processed_count + self.failed_count) > 0 else 0
        }