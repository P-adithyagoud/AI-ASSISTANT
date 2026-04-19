import logging
from flask import Flask, render_template, request, jsonify
from services.commander import IncidentCommander

# Global Configuration
app = Flask(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Orchestrator
commander = IncidentCommander()

@app.route('/')
def index():
    """Serves the main Dashboard UI."""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Primary API Endpoint: Analyzes raw log inputs.
    Expected JSON: { "incident": "raw logs here" }
    """
    try:
        data = request.get_json()
        if not data or 'incident' not in data:
            return jsonify({"success": False, "error": "No incident description provided"}), 400
        
        # Delegate to Orchestration Layer
        result_data, is_fallback = commander.analyze(data['incident'])
        
        if isinstance(result_data, dict) and "error" in result_data:
            return jsonify({"success": False, "error": result_data["error"]}), 500
            
        return jsonify({"success": True, "data": result_data, "fallback": is_fallback})
    
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": f"Internal System Error: {str(e)}"}), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    """
    Feedback API Endpoint: Submits resolution data for KEDB ingestion.
    Expected JSON: Full incident analysis structure + 'incident' field.
    """
    try:
        data = request.get_json()
        if not data or 'incident' not in data:
            return jsonify({"success": False, "error": "No data provided"}), 400
            
        decision = commander.submit_feedback(data)
        return jsonify({"success": True, "data": decision})
    
    except Exception as e:
        logger.error(f"Feedback processing failed: {str(e)}", exc_info=True)
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    # Local development server
    app.run(debug=True, port=5001)
