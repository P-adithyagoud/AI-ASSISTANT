import re

class EmbeddingService:
    """
    Utility Service: Handles text normalization to ensure incident logs
    are optimized for vector retrieval.
    """

    @staticmethod
    def normalize_text(text):
        """
        Cleans and normalizes text for better vector search performance.
        Useful for stripping timestamps, boilerplate, and PII before storage.
        """
        if not text:
            return ""
        
        # Lowercase
        text = text.lower()
        
        # Remove timestamps (basic pattern)
        text = re.sub(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', '[TIMESTAMP]', text)
        
        # Remove noisy characters
        text = re.sub(r'[^a-zA-Z0-9\s.,!?\-]', ' ', text)
        
        # Collapse whitespace
        text = " ".join(text.split())
        
        return text
