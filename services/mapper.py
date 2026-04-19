from typing import Dict, List, Any

class DataMapper:
    """
    Transformation Layer: Decouples LLM/Vector responses from the UI Schema.
    Ensures the Frontend receives a consistent, stable data structure 
    regardless of whether the result came from KEDB, VDB, or LLM Fallback.
    """

    @staticmethod
    def map_fallback_to_plan(raw_fallback: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforms raw Fallback Mode output into the recovery plan schema expected by the UI.
        """
        if not isinstance(raw_fallback, dict) or "error" in raw_fallback:
            return raw_fallback

        # Join possible causes into a single string for legacy UI compatibility
        causes = [
            f"{c.get('cause', 'Unknown')} ({c.get('likelihood', 'N/A')} likelihood)" 
            for c in raw_fallback.get("possible_root_causes", [])
        ]
        root_cause_str = " | ".join(causes) if causes else "Unknown"

        return {
            "summary": raw_fallback.get("incident_summary", "Uncertain Analysis"),
            "root_cause": root_cause_str,
            "resolution_steps": raw_fallback.get("recommended_resolution", []),
            "validation_steps": raw_fallback.get("validation_steps", []),
            "severity": raw_fallback.get("severity", "MEDIUM"),
            "complexity": raw_fallback.get("complexity", "medium"),
            "primary_owner": raw_fallback.get("recommended_owner", "DevOps"),
            "confidence": f"{raw_fallback.get('confidence_score', 0)}%",
            "mode": "fallback",
            "preventive_measures": ["Review system for similar future occurrences"],
            "immediate_actions": [
                {"priority": "medium", "owner": "SRE", "step": "Monitor and Verify Fallback fix"}
            ],
            # Metadata for internal tracking
            "needs_learning": raw_fallback.get("needs_learning", False),
            "vector_db_entry": raw_fallback.get("vector_db_entry")
        }

    @staticmethod
    def map_vdb_match_to_plan(strong_match: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transforms a high-confidence Vector DB match into the standard recovery plan schema.
        """
        return {
            "summary": "Verified Historical Match Found",
            "root_cause": strong_match.get("root_cause", "Historical Root Cause Not Recorded"),
            "resolution_steps": [strong_match.get("resolution", "")],
            "immediate_actions": [
                {"priority": "high", "owner": "SRE", "step": "Review historical resolution"}
            ],
            "complexity": "medium",
            "mode": "full",
            "confidence": "High",
            "severity": strong_match.get("severity", "SEV2"),
            "validation_steps": ["Verify metrics return to baseline"],
            "preventive_measures": ["Review historical incident"],
            "similar_incidents": []
        }

    @staticmethod
    def format_similar_incidents(all_cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Formats a list of retrieved cases into the UI's correlation card structure.
        """
        formatted = []
        for idx, inc in enumerate(all_cases[:3]):
            formatted.append({
                "is_primary_match": (idx == 0),
                "source": inc.get("source", "KEDB"),
                "issue": inc.get("issue", "Historical Issue"),
                "root_cause": inc.get("root_cause", "Found in Database"),
                "resolution": inc.get("resolution", "Refer to history.")
            })
        return formatted
