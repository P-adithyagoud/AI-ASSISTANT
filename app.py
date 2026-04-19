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
        # 1. Normalize query
        query = self.embed.normalize_text(raw_logs)
        
        # 2. Try fetching similar cases (fallback built-in)
        similar_cases = self.vdb.recall_similar(query)
        is_fallback = len(similar_cases) == 0
        
        # 3. Analyze with LLM
        recovery_plan = self.llm.analyze_incident(raw_logs, similar_cases)
        
        # Merge vector DB results into the LLM json output
        if similar_cases and isinstance(recovery_plan, dict):
            # Format the vector db output into what main.js expects
            formatted_similars = []
            for idx, inc in enumerate(similar_cases):
                formatted_similars.append({
                    "is_primary_match": (idx == 0),
                    "source": "LOCAL KEDB", # Example mapping
                    "issue": inc.get("issue", ""),
                    "root_cause": "Found in Vector Database",
                    "resolution": inc.get("resolution", "")
                })
            recovery_plan["similar_incidents"] = formatted_similars

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
