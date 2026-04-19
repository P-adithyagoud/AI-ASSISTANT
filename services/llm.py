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
            ]
        }}
        
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
            print(f"DEBUG: Raw LLM Response: {raw_response}")
            return json.loads(raw_response)
        except Exception as e:
            print(f"LLM Error: {e}")
            return {"error": f"LLM Error: {str(e)}"}

    def evaluate_incident_for_kedb(self, feedback_payload, similar_incidents=None):
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
        You are a production-grade Known Error Database (KEDB) learning engine for an AI Incident Response Assistant.
        Your job is to intelligently decide whether to:
        1. STORE a new known error
        2. UPDATE an existing known error
        3. REJECT storing

        CONTEXT:
        The system receives resolved incidents over time.
        It must learn only HIGH-VALUE, REUSABLE, and STABLE patterns.
        Avoid noise. Avoid duplicates. Prioritize reliability.

        ---
        INPUT INCIDENT (JSON DUMP):
        {payload_str}

        {context}

        ---
        DECISION ENGINE (STRICT LOGIC):
        STEP 1 — HARD FILTER:
        REJECT if ANY:
        * resolution_success == false
        * resolution_type != "permanent"
        * similarity_score < 0.75 AND severity != "HIGH"
        * incident is vague or lacks technical clarity

        STEP 2 — SEVERITY-AWARE GATING:
        ALLOW consideration IF:
        * repeat_count >= 3
          OR
        * severity == "HIGH" AND repeat_count >= 1

        STEP 3 — DEDUPLICATION & UPDATE LOGIC:
        IF existing_kedb_matches is NOT empty:
        * Find best match (highest similarity)
        IF best_match.similarity >= 0.85:
        → DO NOT create new entry
        → UPDATE existing entry
        Update rules:
        * Increase confidence level
        * Merge tags (no duplicates)
        * Improve resolution clarity if new one is better
        * Keep most accurate root cause

        STEP 4 — NEW ENTRY CREATION:
        IF no strong match:
        Normalize incident into reusable pattern:
        * remove user-specific noise
        * keep system + failure + symptom keywords
        * make it generic and reusable

        STEP 5 — CONFIDENCE SCORING:
        Assign confidence:
        HIGH: repeat_count >= 5 OR (repeat_count >= 3 AND similarity_score >= 0.9)
        MEDIUM: repeat_count 3–4
        LOW: repeat_count < 3 AND severity == HIGH

        ---
        STEP 6 — OUTPUT

        You must return a valid JSON object matching ONE of these formats exactly:

        CASE A: STORE NEW
        {{
        "action": "STORE",
        "entry": {{
            "issue": "<clean generalized incident>",
            "root_cause": "<clear root cause>",
            "resolution": "<step-by-step permanent resolution>",
            "severity": "<severity>",
            "tags": ["..."],
            "confidence": "<LOW|MEDIUM|HIGH>"
        }}
        }}

        CASE B: UPDATE EXISTING
        {{
        "action": "UPDATE",
        "target_id": "<existing_kedb_id>",
        "updates": {{
            "confidence": "<updated>",
            "tags": ["merged"],
            "resolution": "<improved if applicable>"
        }}
        }}

        CASE C: REJECT
        {{
        "action": "REJECT",
        "reason": "<clear reason>"
        }}

        IMPORTANT RULES:
        * NEVER create duplicate entries
        * ALWAYS prefer updating over inserting
        * ONLY store stable, reusable knowledge
        * DO NOT store temporary fixes (like restart/redeploy)
        * OUTPUT must be strict JSON only.
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
            print(f"LLM KEDB Error: {e}")
            return {"action": "REJECT", "reason": "LLM evaluation failed."}

    def analyze_fallback(self, incident, similar_incidents=None):
        """
        LLM_FALLBACK mode: Provides structured reasoning when no strong matches exist.
        """
        weak_matches = []
        if similar_incidents:
            for inc in similar_incidents:
                weak_matches.append({
                    "summary": inc.get("issue", "Unknown"),
                    "similarity": inc.get("relevance", 0)
                })

        input_payload = {
            "incident": incident,
            "weak_matches": weak_matches
        }

        prompt = f"""
        You are an AI Incident Response Assistant operating in FALLBACK MODE.
        No strong matches were found in KEDB or Vector DB.
        However, weak contextual matches (if provided) may still contain useful signals.

        Your job is to provide a structured, realistic, and cautious analysis AND prepare the incident for vector database storage.

        ---
        INPUT:
        {json.dumps(input_payload, indent=2)}

        ---
        TASK:
        1. Normalize the incident into a clear technical summary.
        2. Identify 2–4 POSSIBLE root causes:
        * Rank by likelihood
        * Avoid certainty
        3. Generate step-by-step resolution:
        * Start with safest steps
        * Include validation steps
        * Avoid destructive actions
        4. Assign:
        * severity (LOW | MEDIUM | HIGH)
        * complexity (EASY | MEDIUM | HARD)
        5. Generate confidence score based on clarity + signals (0-100)

        ---
        LEARNING DECISION:
        Set "needs_learning" = true ONLY IF:
        * incident is clear
        * resolution is meaningful
        * not vague or generic

        ---
        STEP 6 — VECTOR DB PREPARATION:
        IF needs_learning == true:
        Create embedding-ready document:
        "Incident: <incident_summary>. Root Cause: <top cause>. Resolution: <resolution summary>. Severity: <severity>. Tags: <tags>."

        Also generate metadata:
        {{
        "severity": "<severity>",
        "complexity": "<complexity>",
        "source": "llm_fallback",
        "confidence": <confidence_score>
        }}

        ---
        OUTPUT FORMAT (STRICT JSON):
        {{
        "source": "LLM_FALLBACK",
        "incident_summary": "<clean normalized version>",
        "possible_root_causes": [
        {{
            "cause": "<text>",
            "likelihood": "HIGH | MEDIUM | LOW"
        }}
        ],
        "recommended_resolution": [
        "<step 1>",
        "<step 2>"
        ],
        "validation_steps": [
        "<how to confirm fix>"
        ],
        "severity": "<LOW | MEDIUM | HIGH>",
        "complexity": "<EASY | MEDIUM | HARD>",
        "confidence_score": <0-100>,
        "needs_learning": <true|false>,
        "vector_db_entry": {{
        "document": "<embedding-ready text>",
        "metadata": {{
            "severity": "<severity>",
            "complexity": "<complexity>",
            "source": "llm_fallback",
            "confidence": <confidence_score>
        }}
        }}
        }}

        ---
        IMPORTANT RULES:
        * DO NOT directly store anything
        * Only prepare data for storage
        * If needs_learning == false → set vector_db_entry = null
        * Keep embedding text natural and complete
        * Output ONLY valid JSON
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            raw_response = chat_completion.choices[0].message.content
            print(f"DEBUG: Fallback Raw LLM Response: {raw_response}")
            return json.loads(raw_response)
        except Exception as e:
            print(f"LLM Fallback Error: {e}")
            return {"error": f"Fallback mode failed: {str(e)}"}
