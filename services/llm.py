import os
from groq import Groq
from config import GROQ_API_KEY

class LLMService:
    """
    Intelligence Layer: Handles advanced incident analysis and resolution path generation.
    Uses Groq for ultra-fast response times.
    """
    
    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.model = "llama-3.3-70b-versatile"

    def analyze_incident(self, current_incident, similar_incidents=None):
        """
        Generates a targeted resolution plan. 
        Works in Zero-Shot mode if no similar_incidents are provided.
        """
        context = ""
        if similar_incidents:
            context = "\n### Historical Context (Past Similar Incidents):\n"
            for i, inc in enumerate(similar_incidents):
                context += f"{i+1}. Issue: {inc.get('issue')}\n   Root Cause: {inc.get('root_cause')}\n   Resolution: {inc.get('resolution')}\n\n"

        prompt = f"""
        You are an Expert SRE Incident Commander. Analyze the following incident and provide a recovery plan.
        
        {context}
        
        ### Current Incident:
        {current_incident}
        
        ### Instructions:
        1. Identify the likely Root Cause.
        2. Provide Immediate Actions.
        3. Recommend a Long-term Resolution.
        4. Provide an 'Expert Confidence' level (0-100%) for your assessment.
        
        Output in professional markdown format. Use bold headers and clean lists.
        """

        try:
            chat_completion = self.client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model=self.model,
                temperature=0.2,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            return f"Error in LLM analysis: {str(e)}"
