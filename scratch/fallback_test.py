import os
import sys
import json
sys.path.insert(0, os.getcwd())
from services.llm import LLMService
from app import commander

def test_fallback_mode():
    print("--- Testing Standalone analyze_fallback ---")
    llm = LLMService()
    
    unique_incident = "Strange blue smoke coming from the primary load balancer rack"
    
    result = llm.analyze_fallback(unique_incident)
    print(json.dumps(result, indent=2))
    
    print("\n--- Testing Integrated Commander.analyze (Fallback branch) ---")
    # This should trigger fallback mode because there's no way this matches a DB entry
    final_output, is_fallback = commander.analyze(unique_incident)
    
    print(f"Is Fallback Mode active? {is_fallback}")
    print(f"Confidence: {final_output.get('confidence')}")
    print(f"Summary: {final_output.get('summary')}")
    print(f"Root Cause (Mapped): {final_output.get('root_cause')}")
    print(f"Needs Learning: {final_output.get('needs_learning')}")
    
    if final_output.get('vector_db_entry'):
        print("\nVector DB Preparation Document:")
        print(final_output['vector_db_entry']['document'])

if __name__ == "__main__":
    test_fallback_mode()
