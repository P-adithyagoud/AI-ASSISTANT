import json
import os
import logging
from typing import List, Dict, Any

# Configure Logging
logger = logging.getLogger(__name__)

class LocalKEDBService:
    """
    Legacy Knowledge Layer: Interfaces with the local data/kedb.json.
    Provides verified gold-standard incident resolutions.
    """

    def __init__(self, db_path: str = "data/kedb.json"):
        """Initializes the service and verifies the KEDB file exists."""
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            logger.warning(f"KEDB file not found at {self.db_path}. Initializing empty store.")
            self._write_db([])

    def _read_db(self) -> List[Dict[str, Any]]:
        """Reads the raw KEDB dataset from disk."""
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading KEDB: {str(e)}")
            return []

    def _write_db(self, data: List[Dict[str, Any]]):
        """Writes the dataset back to disk."""
        try:
            with open(self.db_path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Error writing KEDB: {str(e)}")

    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Performs a simple keyword-based search across the local KEDB.
        
        Args:
            query: The raw input incident text.
            
        Returns:
            A list of matching KEDB entries.
        """
        logger.info(f"Scanning Local KEDB for matches to: {query[:30]}...")
        db = self._read_db()
        results = []
        
        query_words = set(query.lower().split())
        
        for entry in db:
            issue_words = set(entry.get("issue", "").lower().split())
            # Match if there's any intersection of non-trivial words
            if query_words.intersection(issue_words):
                results.append({
                    "issue": entry.get("issue"),
                    "root_cause": entry.get("root_cause"),
                    "resolution": entry.get("resolution"),
                    "source": "KEDB",
                    "relevance": 1.0  # Local matches are treated as exact/gold standard
                })
        
        return results
