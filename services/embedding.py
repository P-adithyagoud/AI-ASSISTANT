import re
import logging
from typing import Optional

# Configure Logging
logger = logging.getLogger(__name__)

class EmbeddingService:
    """
    Preprocessing Layer: Handles text normalization and cleanup.
    Ensures that raw logs are stripped of noise (timestamps, PII, punctuation)
    before being sent to the Vector DB or LLM for analysis.
    """

    @staticmethod
    def normalize_text(text: Optional[str]) -> str:
        """
        Cleans and normalizes text for optimal vector search performance.
        
        Args:
            text: Raw input text from logs or symptoms.
            
        Returns:
            A cleaned, lower-cased, and keyword-focused version of the text.
        """
        if not text:
            return ""
        
        try:
            # 1. Lowercase
            text = text.lower()
            
            # 2. Redact timestamps (e.g. 2026-04-19 08:00:00)
            text = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', '[TIMESTAMP]', text)
            
            # 3. Filter noise (keep alphanumeric, space, and basic punctuation)
            text = re.sub(r'[^a-zA-Z0-9\s.,!?\-]', ' ', text)
            
            # 4. Collapse whitespace
            text = " ".join(text.split())
            
            return text
            
        except Exception as e:
            logger.error(f"Text normalization failed: {str(e)}")
            return text if text else ""
