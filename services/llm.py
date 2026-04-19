import os
import json
from groq import Groq
from config import GROQ_API_KEY

class LLMService:
    """
    Intelligence Layer: Handles advanced incident analysis using Groq JSON mode.
    """
    
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

    def analyze_incident(self, current_incident, similar_incidents=None):
        context = ""
        if similar_incidents:
            context = "\n### Historical Context (Past Similar Incidents from both LOCAL KEDB and VECTOR DB):\n"
            for i, inc in enumerate(similar_incidents):
                source = inc.get('source', 'Unknown')
                context += f"Incident {i+1} [Source: {source}]:\n"
                context += f"Issue: {inc.get('issue')}\n"
                context += f"Root Cause: {inc.get('root_cause', 'Unknown')}\n"
                context += f"Resolution/Context: {inc.get('resolution')}\n\n"

        prompt = f"""
        You are an Expert SRE Incident Commander. Analyze the following incident and provide a structured recovery plan in JSON format.
        
        {context}
        
        ### Current Incident:
        {current_incident}
        
        ### JSON Constraints
        You must return a valid JSON object matching this exact structure containing the keys:
        {{
            "severity": "SEV1, SEV2, or SEV3",
            "complexity": "easy, medium, or hard",
            "mode": "full or partial",
            "confidence": "Low, Medium, or High",
            "summary": "Brief 1-sentence summary of the incident",
            "root_cause": "Detailed explanation of the root cause",
            "immediate_actions": [
                {{
                    "priority": "high or medium",
                    "owner": "DevOps, Backend, etc.",
                    "step": "Specific mitigation step"
                }}
            ],
            "resolution_steps": [
                "Step 1 for resolution",
                "Step 2 for resolution"
            ],
            "validation_steps": [
                "Step 1 to validate"
            ],
            "preventive_measures": [
                "Preventative measure 1"
            ],
            "similar_incidents": [
                {{
                    "is_primary_match": true,
                    "source": "Source string EXACTLY as provided (e.g. LOCAL KEDB or VECTOR DB)",
                    "issue": "Historical issue text",
                    "root_cause": "Historical root cause",
                    "resolution": "Historical resolution"
                }}
            ]
        }}
        
        IMPORTANT RULES FOR `similar_incidents`:
        - Out of the incidents provided in the Historical Context (which contains items tagged as VECTOR DB and/or LOCAL KEDB), you MUST select exactly the BEST 3 most relevant incidents.
        - You MUST include a mix of sources if possible! Try to include at least 1 incident with "source": "VECTOR DB" and 1 incident with "source": "LOCAL KEDB".
        - Do not hallucinate sources. Use the exact "Source: XYZ" provided in the prompt brackets.
        
        Do not output any markdown code blocks (e.g. ```json), just raw JSON.
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            raw_response = chat_completion.choices[0].message.content
            return json.loads(raw_response)
        except Exception as e:
            print(f"LLM Error: {e}")
            return {"error": "Failed to analyze incident."}
