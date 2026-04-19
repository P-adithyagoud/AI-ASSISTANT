import os
import sys
import json
sys.path.insert(0, os.getcwd())
from services.llm import LLMService

def test_complexity_engine():
    llm = LLMService()
    
    test_cases = [
        {
            "incident": "Single pod restart in dev environment",
            "root_cause": "OOMKill due to temporary memory spike",
            "resolution_steps": "Restarted pod and increased memory limit slightly",
            "tags": ["kubernetes", "dev"],
            "severity": "LOW"
        },
        {
            "incident": "System-wide database connectivity failure in production",
            "root_cause": "Primary database instance failed due to disk corruption, with standby replica failing to promote",
            "resolution_steps": "Manually promoted secondary replica and restored primary from snapshot",
            "tags": ["database", "production", "outage"],
            "severity": "HIGH"
        }
    ]
    
    print("Testing Standalone Complexity Engine...")
    for case in test_cases:
        print(f"\nEvaluating: {case['incident']}")
        result = llm.classify_complexity(
            case['incident'], 
            case['root_cause'], 
            case['resolution_steps'], 
            case['tags'], 
            case['severity']
        )
        print(json.dumps(result, indent=2))

    print("\nTesting Integrated Analysis Engine...")
    analyze_result = llm.analyze_incident("Production API returning 500 across all regions")
    print(f"Complexity Level: {analyze_result.get('complexity', {}).get('level')}")
    print(json.dumps(analyze_result.get('complexity'), indent=2))

if __name__ == "__main__":
    test_complexity_engine()
