import logging
from typing import Dict, Tuple, Any, List

from services.llm import LLMService
from services.vector_db import VectorDBService
from services.embedding import EmbeddingService
from services.kedb import LocalKEDBService
from services.mapper import DataMapper

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IncidentCommander:
    """
    Orchestration Layer: Coordinates the retrieval, analysis, and feedback flow
    of the Incident Response Assistant.
    """

    def __init__(self):
        self.llm = LLMService()
        self.vdb = VectorDBService()
        self.embed = EmbeddingService()
        self.kedb = LocalKEDBService()
        self.mapper = DataMapper()

    def analyze(self, raw_logs: str) -> Tuple[Dict[str, Any], bool]:
        """
        Executes the full hybrid-retrieval and analysis pipeline.
        
        Args:
            raw_logs: The raw text input containing logs or symptoms.
            
        Returns:
            A tuple of (recovery_plan_dict, transition_is_fallback_flag)
        """
        # 1. Normalize query
        query = self.embed.normalize_text(raw_logs)
        logger.info(f"Analyzing incident with normalized query: {query[:50]}...")
        
        # 2. Hybrid Retrieval (Vector DB + KEDB)
        vdb_cases = self.vdb.recall_similar(query)
        for case in vdb_cases:
            case["source"] = "VECTOR DB"
            
        kedb_cases = self.kedb.search(raw_logs)
        all_cases = vdb_cases + kedb_cases
        
        logger.info(f"Retrieved {len(kedb_cases)} KEDB entries and {len(vdb_cases)} VDB entries.")
        
        is_fallback = len(all_cases) == 0

        # 3. Check for High-Confidence Match (Hot Path)
        strong_match = self._find_strong_match(vdb_cases)
        if strong_match:
            logger.info("Found high-confidence historical match. Skipping LLM generation.")
            plan = self.mapper.map_vdb_match_to_plan(strong_match)
            return plan, is_fallback

        # 4. LLM-Driven Analysis (Fallback/Generation Path)
        logger.info("Executing LLM-driven diagnostic analysis.")
        raw_llm_output = self.llm.analyze_fallback(raw_logs, all_cases)
        
        # 5. Transform and Inject Context
        recovery_plan = self.mapper.map_fallback_to_plan(raw_llm_output)
        
        if isinstance(recovery_plan, dict) and "error" not in recovery_plan:
            recovery_plan["similar_incidents"] = self.mapper.format_similar_incidents(all_cases)
            
        return recovery_plan, is_fallback

    def submit_feedback(self, feedback_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Processes feedback from the user to potentially update the KEDB.
        """
        raw_issue = feedback_payload.get("incident", "")
        if not raw_issue:
            return {"action": "REJECT", "reason": "No incident description provided."}
            
        query = self.embed.normalize_text(raw_issue)
        logger.info(f"Processing feedback for: {raw_issue[:50]}...")

        # Search existing knowledge for deduplication
        all_cases = self.vdb.recall_similar(query) + self.kedb.search(raw_issue)
        
        decision = self.llm.evaluate_incident_for_kedb(feedback_payload, all_cases)
        logger.info(f"Knowledge ingestion decision: {decision.get('action')}")
        
        self._execute_ingestion_action(decision, query, raw_issue, feedback_payload)
        return decision

    def _find_strong_match(self, cases: List[Dict[str, Any]]) -> Any:
        """Heuristic to identify a verified match based on relevance score."""
        if not cases:
            return None
        best = cases[0]
        relevance = best.get("relevance", 0)
        return best if (isinstance(relevance, (int, float)) and relevance >= 0.85) else None

    def _execute_ingestion_action(self, decision, query, raw_issue, payload):
        """Helper to commit knowledge changes to the vector store."""
        action = decision.get("action")
        entry = decision.get("entry", {})
        
        if action in ["STORE", "UPDATE"]:
            self.vdb.store_incident(
                embedding=query,
                issue=entry.get("issue", raw_issue),
                root_cause=entry.get("root_cause", payload.get("root_cause", "Unknown")),
                resolution=entry.get("resolution", "Refer to system logs."),
                severity=entry.get("severity", payload.get("severity", "MEDIUM")),
                tags=entry.get("tags", [])
            )
