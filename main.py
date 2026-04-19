import sys
import os
from services.llm import LLMService

class IncidentCommander:
    """
    Core Application: Orchestrates the workflow from log ingestion to resolution.
    Simplified version without Vector DB.
    """
    
    def __init__(self):
        self.llm = LLMService()

    def handle_incident(self, raw_logs):
        """
        The pipeline: Analyze -> Resolve.
        """
        print("\n--- Incident Investigation Started ---")
        
        # 1. Analyze with LLM 
        print("Generating resolution plan using Groq...")
        recovery_plan = self.llm.analyze_incident(raw_logs)
        
        print("\n--- Recovery Plan Generated ---\n")
        print(recovery_plan)
        
        return recovery_plan

def main():
    commander = IncidentCommander()
    
    print("SRE Commander | Expert Incident Response Agent")
    print("Type your incident logs/description below (or 'exit' to quit):")
    
    while True:
        try:
            user_input = input("\n> ")
            if user_input.lower() == 'exit':
                break
            
            if not user_input.strip():
                continue
                
            commander.handle_incident(user_input)
            
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()
