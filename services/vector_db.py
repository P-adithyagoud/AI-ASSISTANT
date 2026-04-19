import os
import requests
from config import VECTORIZE_API_KEY, HINDSIGHT_URL

# Optional: Try importing hindsight_client if available
try:
    from hindsight_client import Hindsight
    HINDSIGHT_AVAILABLE = True
except ImportError:
    HINDSIGHT_AVAILABLE = False

class VectorDBService:
    """
    Memory Layer: Manages retrieval of historical incidents.
    Powered by Hindsight (Vectorize.io) with strict fallback logic.
    """
    
    def __init__(self, bank_id="sre-incidents"):
        self.bank_id = bank_id
        self.client = None
        
        # We only initialize if keys are present
        if VECTORIZE_API_KEY and HINDSIGHT_URL and HINDSIGHT_AVAILABLE:
            try:
                self.client = Hindsight(base_url=HINDSIGHT_URL, api_key=VECTORIZE_API_KEY)
            except Exception as e:
                print(f"Warning: Failed to initialize Hindsight client. {e}")

    def recall_similar(self, query, top_n=3):
        """
        Recalls the most relevant past incidents based on a query.
        Returns an empty list [] if anything fails (Fallback mode).
        """
        if not self.client:
            print("Vector DB client not initialized. Falling back.")
            return []

        try:
            results = self.client.recall(bank_id=self.bank_id, query=query)
            
            parsed_results = []
            for item in results[:top_n]:
                parsed_results.append({
                    "issue": item.get("content", ""),
                    "relevance": item.get("relevance", 0),
                    "resolution": item.get("resolution", "Refer to history.") # Just in case it has it natively
                })
            return parsed_results
        except Exception as e:
            print(f"Error recalling memory from Vector DB: {str(e)}. Falling back.")
            return []
