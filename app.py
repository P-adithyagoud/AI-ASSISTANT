from flask import Flask, render_template, request, jsonify
from services.llm import LLMService
import os

# Application Entry Point
app = Flask(__name__)

from services.vector_db import VectorDBService
from services.embedding import EmbeddingService
from services.kedb import LocalKEDBService

class IncidentCommander:
    def __init__(self):
        self.llm = LLMService()
        self.vdb = VectorDBService()
        self.embed = EmbeddingService()
        self.kedb = LocalKEDBService()

    def analyze(self, raw_logs):
        # 1. Normalize query (Embedding)
        query = self.embed.normalize_text(raw_logs)
        
        # 2. Try fetching similar cases from Vector DB and KEDB
        similar_cases = self.vdb.recall_similar(query)
        
        # We ensure vector DB incidents are marked before merging
        for case in similar_cases:
            case["source"] = "VECTOR DB"
            
        kedb_cases = self.kedb.search(raw_logs)
        all_cases = similar_cases + kedb_cases  # Put VDB first
        
        print(f"DEBUG: Retrieved {len(kedb_cases)} from KEDB and {len(similar_cases)} from VDB.")
        
        is_fallback = len(all_cases) == 0
        
        # 3. IF strong match exists (score >= 0.85):
        strong_match = None
        if similar_cases:
            best_match = similar_cases[0]
            # Handle float comparison safely
            if isinstance(best_match.get("relevance"), (int, float)) and best_match.get("relevance") >= 0.85:
                strong_match = best_match

        if strong_match:
            print("Strong match found in Vector DB. Returning stored result.")
            recovery_plan = {
                "summary": "Match found in Vector DB",
                "root_cause": strong_match.get("root_cause", "Historical Root Cause Not Recorded"),
                "resolution_steps": [strong_match.get("resolution", "")],
                "immediate_actions": [{"priority": "high", "owner": "SRE", "step": "Review historical resolution"}],
                "complexity": "medium",
                "mode": "full",
                "confidence": "High",
                "severity": strong_match.get("severity", "SEV2"),
                "validation_steps": ["Verify metrics return to baseline"],
                "preventive_measures": ["Review historical incident"],
                "similar_incidents": []
            }
            return recovery_plan, is_fallback
            
        # 4. ELSE: Analyze with dedicated Fallback Mode or Standard Analyze
        if strong_match:
            # We already returned above if strong_match existed
            pass
            
        # Call Fallback Mode if no strong matches were found
        raw_fallback = self.llm.analyze_fallback(raw_logs, all_cases)
        
        # MAP Fallback keys to UI-compatible keys for "Old Output" stability
        if isinstance(raw_fallback, dict) and "error" not in raw_fallback:
            # Join possible causes into a single string for UI compatibility
            causes = [f"{c['cause']} ({c['likelihood']} likelihood)" for c in raw_fallback.get("possible_root_causes", [])]
            root_cause_str = " | ".join(causes) if causes else "Unknown"
            
            recovery_plan = {
                "summary": raw_fallback.get("incident_summary"),
                "root_cause": root_cause_str,
                "resolution_steps": raw_fallback.get("recommended_resolution", []),
                "validation_steps": raw_fallback.get("validation_steps", []),
                "severity": raw_fallback.get("severity", "MEDIUM"),
                "complexity": raw_fallback.get("complexity", "medium"),
                "primary_owner": raw_fallback.get("recommended_owner", "DevOps"),
                "confidence": f"{raw_fallback.get('confidence_score', 0)}%",
                "mode": "fallback",
                "preventive_measures": ["Review system for similar future occurrences"],
                "immediate_actions": [{"priority": "medium", "owner": "SRE", "step": "Monitor and Verify Fallback fix"}],
                # Pass learning metadata through for future tracking
                "needs_learning": raw_fallback.get("needs_learning", False),
                "vector_db_entry": raw_fallback.get("vector_db_entry")
            }
        else:
            recovery_plan = raw_fallback

        # PARSE LLM response and handle Vector DB results mapping
        if isinstance(recovery_plan, dict) and "error" not in recovery_plan:
            # Restore manual injection to ensure "old" stable output format for UI
            if all_cases:
                formatted_similars = []
                # Take top 3 total from the merged results
                for idx, inc in enumerate(all_cases[:3]):
                    formatted_similars.append({
                        "is_primary_match": (idx == 0),
                        "source": inc.get("source", "KEDB"),
                        "issue": inc.get("issue", "Historical Issue"),
                        "root_cause": inc.get("root_cause", "Found in Database"),
                        "resolution": inc.get("resolution", "Refer to history.")
                    })
                recovery_plan["similar_incidents"] = formatted_similars
            
            # KEDB Learning Engine: Auto-storage has been deliberately removed.
            # Resolved incidents must be submitted via /feedback to be safely ingested.
            pass

        return recovery_plan, is_fallback

    def submit_feedback(self, feedback_payload):
        raw_issue = feedback_payload.get("incident", "")
        if not raw_issue:
            return {"action": "REJECT", "reason": "No incident description provided."}
            
        query = self.embed.normalize_text(raw_issue)
        vdb_cases = self.vdb.recall_similar(query)
        for case in vdb_cases:
            case["source"] = "VECTOR DB"
        kedb_cases = self.kedb.search(raw_issue)
        all_cases = vdb_cases + kedb_cases
        
        decision = self.llm.evaluate_incident_for_kedb(feedback_payload, all_cases)
        print(f"KEDB Engine Decision: {decision}")
        
        action = decision.get("action")
        if action == "STORE":
            entry = decision.get("entry", {})
            self.vdb.store_incident(
                embedding=query,
                issue=entry.get("issue", raw_issue),
                root_cause=entry.get("root_cause", "Unknown"),
                resolution=entry.get("resolution", "Unknown"),
                severity=entry.get("severity", "MEDIUM"),
                tags=entry.get("tags", [])
            )
        elif action == "UPDATE":
            updates = decision.get("updates", {})
            # Since Hindsight retains via semantics, we store the updated version
            res_steps = feedback_payload.get("resolution_steps", "Updated Resolution")
            res_str = " ".join(res_steps) if isinstance(res_steps, list) else str(res_steps)
            self.vdb.store_incident(
                embedding=query,
                issue=raw_issue,
                root_cause=feedback_payload.get("root_cause", "Updated Issue"),
                resolution=updates.get("resolution", res_str),
                severity=feedback_payload.get("severity", "MEDIUM"),
                tags=updates.get("tags", [])
            )
            
        return decision

commander = IncidentCommander()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        if not data or 'incident' not in data:
            return jsonify({"success": False, "error": "No incident data provided"}), 400
        
        result_data, is_fallback = commander.analyze(data['incident'])
        
        if isinstance(result_data, dict) and "error" in result_data:
            return jsonify({"success": False, "error": result_data["error"]}), 500
            
        return jsonify({"success": True, "data": result_data, "fallback": is_fallback})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        data = request.get_json()
        if not data or 'incident' not in data:
            return jsonify({"success": False, "error": "No incident data provided"}), 400
            
        decision = commander.submit_feedback(data)
        return jsonify({"success": True, "data": decision})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
