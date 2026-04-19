from flask import Flask, render_template, request, jsonify
from services.llm import LLMService
import os

# Application Entry Point
app = Flask(__name__)

class IncidentCommander:
    def __init__(self):
        # Only LLM is needed now
        self.llm = LLMService()

    def analyze(self, raw_logs):
        # Direct Zero-Shot analysis
        recovery_plan = self.llm.analyze_incident(raw_logs)
        
        return {
            "analysis": recovery_plan,
            "similar_incidents_count": 0  # Fixed to 0 for this version
        }

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
        
        result = commander.analyze(data['incident'])
        return jsonify({"success": True, "data": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)
