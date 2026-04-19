import os
import logging
from typing import Dict, List, Any, Optional
from hindsight_client import Hindsight
from config import VECTORIZE_API_KEY, HINDSIGHT_URL

# Configure Logging
logger = logging.getLogger(__name__)

class VectorDBService:
    """
    Persistence Layer: Interfaces with Hindsight (Vectorize.io) for semantic memory.
    Handles storage and retrieval of historical incident knowledge.
    """

    def __init__(self):
        """Initializes the Hindsight client using environment credentials."""
        self.client = Hindsight(
            api_key=VECTORIZE_API_KEY,
            base_url=HINDSIGHT_URL
        )

    def recall_similar(self, query_text: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Retrieves top semantically similar incidents from the vector store.
        
        Args:
            query_text: Normalized incident logs/symptoms.
            limit: Number of results to return.
            
        Returns:
            A list of matching incident records with relevance scores.
        """
        try:
            logger.info(f"Querying Hindsight for: {query_text[:50]}...")
            # Use 'recall' method as per hindsight_client API
            response = self.client.recall(prompt=query_text)
            
            formatted = []
            # Results are in the response object
            for res in response[:limit]:
                formatted.append({
                    "issue": res.document,
                    "relevance": getattr(res, 'score', 0.8), # Default confidence if score missing
                    "root_cause": res.metadata.get("root_cause", "Historical context"),
                    "resolution": res.metadata.get("resolution", "Refer to history"),
                    "severity": res.metadata.get("severity", "MEDIUM"),
                    "source": "VECTOR DB"
                })
            return formatted
            
        except Exception as e:
            logger.error(f"Hindsight recall failed: {str(e)}")
            return []

    def store_incident(self, embedding: str, issue: str, root_cause: str, resolution: str, severity: str, tags: List[str]) -> bool:
        """
        Persists a new incident resolution into the vector store.
        """
        try:
            metadata = {
                "root_cause": root_cause,
                "resolution": resolution,
                "severity": severity,
                "tags": tags,
                "source": "LEARNED_CORE"
            }
            
            logger.info(f"Retaining knowledge in Hindsight: {issue[:50]}")
            # Use 'retain' method as per hindsight_client API
            self.client.retain(
                document=f"Incident: {issue}. Root Cause: {root_cause}. Resolution: {resolution}",
                metadata=metadata
            )
            return True
            
        except Exception as e:
            logger.error(f"Hindsight retention failed: {str(e)}")
            return False
