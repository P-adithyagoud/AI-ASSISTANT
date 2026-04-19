import os
import json
import logging
from typing import Dict, List, Any, Optional
from groq import Groq
from config import GROQ_API_KEY

# Configure Logging
logger = logging.getLogger(__name__)

class LLMService:
    """
    Intelligence Layer: Handles advanced incident analysis using Groq JSON mode.
    Communicates with Llama-3-70b to provide diagnostic reasoning and 
    knowledge-base ingestion decisions.
    """
    
    def __init__(self):
        """Initializes the Groq client and sets the default model."""
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

    def analyze_incident(self, current_incident: str, similar_incidents: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Analyzes a live incident using historical context from the vector database.
        
        Args:
            current_incident: The raw text/logs of the current issue.
            similar_incidents: A list of historical matches for context.
            
        Returns:
            A structured recovery plan as a dictionary.
        """
        context = ""
        if similar_incidents:
            context = "\n### Historical Context (Past Similar Incidents):\n"
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
        You must return a valid JSON object matching this exact structure:
        {{
            "severity": "SEV1, SEV2, or SEV3",
            "complexity": "easy, medium, or hard",
            "mode": "full or partial",
            "confidence": "Low, Medium, or High",
            "primary_owner": "Frontend | Backend | DevOps | Security",
            "summary": "Brief 1-sentence summary",
            "root_cause": "Detailed explanation",
            "immediate_actions": [{{"priority": "high", "owner": "group", "step": "step"}}],
            "resolution_steps": ["step 1", "step 2"],
            "validation_steps": ["step 1"],
            "preventive_measures": ["measure 1"]
        }}
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            raw_response = chat_completion.choices[0].message.content
            logger.debug(f"LLM Response: {raw_response}")
            return json.loads(raw_response)
        except Exception as e:
            logger.error(f"Analysis iteration failed: {str(e)}")
            return {"error": f"LLM Generation Error: {str(e)}"}

    def evaluate_incident_for_kedb(self, feedback_payload: Dict[str, Any], similar_incidents: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Decides if a resolved incident should be ingested into the KEDB or updated.
        
        Args:
            feedback_payload: The data submitted by the user.
            similar_incidents: Existing knowledge to prevent duplicates.
            
        Returns:
            A decision dictionary: { "action": "STORE|UPDATE|REJECT", ... }
        """
        context = ""
        if similar_incidents:
            context = "\n### existing_kedb_matches:\n"
            for i, inc in enumerate(similar_incidents):
                source = inc.get('source', 'Unknown')
                context += f"Match {i+1} [{source}]:\n"
                context += f"Issue: {inc.get('issue')}\n"
                context += f"Root Cause: {inc.get('root_cause', 'Unknown')}\n"
                context += f"Resolution/Context: {inc.get('resolution')}\n\n"

        payload_str = json.dumps(feedback_payload, indent=2)

        prompt = f"""
        You are a KEDB learning engine. Decide whether to STORE, UPDATE or REJECT.
        INPUT: {payload_str}
        {context}
        
        Rules:
        - HIGH-VALUE Patterns only.
        - DEDUPLICATE: If match exists (similarity >= 0.85), UPDATE it.
        - Normalize noisy data.
        
        Output valid JSON with "action", "entry" (if STORE), "updates" (if UPDATE), or "reason" (if REJECT).
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            raw_response = chat_completion.choices[0].message.content
            return json.loads(raw_response)
        except Exception as e:
            logger.error(f"KEDB Evaluation failed: {str(e)}")
            return {"action": "REJECT", "reason": "Evaluation engine error."}

    def analyze_fallback(self, incident: str, similar_incidents: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Provides structured reasoning for first-of-their-kind incidents 
        where no strong matches exist in the databases.
        """
        weak_matches = []
        if similar_incidents:
            for inc in similar_incidents:
                weak_matches.append({
                    "summary": inc.get("issue", "Unknown"),
                    "similarity": inc.get("relevance", 0)
                })

        input_payload = {"incident": incident, "weak_matches": weak_matches}

        prompt = f"""
        You are an Incident Responder in FALLBACK MODE (zero strong database matches).
        
        TASK:
        1. Technical Summary.
        2. Rank 2-4 possible root causes.
        3. Step-by-step resolution.
        4. Preparatory Vector DB entry.
        
        INPUT: {json.dumps(input_payload)}
        
        Output STRICT JSON.
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            raw_response = chat_completion.choices[0].message.content
            logger.debug(f"Fallback response generated.")
            return json.loads(raw_response)
        except Exception as e:
            logger.error(f"Fallback analysis failed: {str(e)}")
            return {"error": f"Fallback mode failure: {str(e)}"}
