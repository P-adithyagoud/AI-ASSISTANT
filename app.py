from flask import Flask, render_template, request, jsonify
from services.llm import LLMService
import os

# Application Entry Point
app = Flask(__name__)

from services.vector_db import VectorDBService
from services.embedding import EmbeddingService

class IncidentCommander:
    def __init__(self):
        self.llm = LLMService()
        self.vdb = VectorDBService()
        self.embed = EmbeddingService()

    def analyze(self, raw_logs):
        # 1. Normalize query (Embedding)
        query = self.embed.normalize_text(raw_logs)
        
        # 2. Try fetching similar cases
        similar_cases = self.vdb.recall_similar(query)
        is_fallback = len(similar_cases) == 0
        
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
            
        # 4. ELSE: Analyze with LLM
        recovery_plan = self.llm.analyze_incident(raw_logs, similar_cases)
        
        # PARSE LLM response and handle Vector DB results mapping
        if isinstance(recovery_plan, dict) and "error" not in recovery_plan:
            # Format the vector db output into what main.js expects
            if similar_cases:
                formatted_similars = []
                for idx, inc in enumerate(similar_cases):
                    formatted_similars.append({
                        "is_primary_match": (idx == 0),
                        "source": "LOCAL KEDB",
                        "issue": inc.get("issue", "Historical Issue"),
                        "root_cause": inc.get("root_cause", "Found in Vector Database"),
                        "resolution": inc.get("resolution", "Refer to history.")
                    })
                recovery_plan["similar_incidents"] = formatted_similars

            # CALL store_incident() before returning
            issue_summary = recovery_plan.get("summary", "Unknown Issue")
            root_cause = recovery_plan.get("root_cause", "Unknown Root Cause")
            
            # Combine resolution steps into a single string for storage
            res_steps = recovery_plan.get("resolution_steps", [])
            resolution = " ".join(res_steps) if isinstance(res_steps, list) else str(res_steps)
            
            severity = recovery_plan.get("severity", "SEV3")
            tags = ["incident", severity.lower()]
            
            self.vdb.store_incident(
                embedding=query,
                issue=issue_summary,
                root_cause=root_cause,
                resolution=resolution,
                severity=severity,
                tags=tags
            )

        return recovery_plan, is_fallback

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
        return jsonify({"success": True, "data": result_data, "fallback": is_fallback})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
