import json
import os

class LocalKEDBService:
    """
    Local KEDB Layer: Simulates retrieving "Gold Standard" incidents from a Local JSON file.
    """
    
    def __init__(self, filepath="data/kedb.json"):
        self.filepath = filepath
        self.incidents = self._load_data()

    def _load_data(self):
        if not os.path.exists(self.filepath):
            print(f"KEDB file {self.filepath} not found.")
            return []
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading KEDB data: {e}")
            return []

    def search(self, query, top_n=3):
        """
        A rudimentary search that looks for query tokens in the KEDB incidents.
        Since it's a mock, we just return up to top_n incidents that match some keywords, or fallback to the first top_n.
        """
        if not self.incidents:
            return []
        
        query_terms = set(query.lower().split())
        scored_incidents = []
        
        for inc in self.incidents:
            score = 0
            # Check issue and root cause
            text_to_search = (inc.get("issue", "") + " " + inc.get("root_cause", "")).lower()
            tags = [t.lower() for t in inc.get("tags", [])]
            
            for term in query_terms:
                if len(term) > 3 and term in text_to_search:
                    score += 1
                if term in tags:
                    score += 2
            
            # Map attributes to standard format required by LLM
            formatted_inc = {
                "source": "LOCAL KEDB",
                "issue": inc.get("issue", ""),
                "root_cause": inc.get("root_cause", ""),
                "resolution": inc.get("resolution", ""),
                "relevance": score # Keep score to sort
            }
            scored_incidents.append(formatted_inc)
            
        # Sort by highest score
        scored_incidents.sort(key=lambda x: x["relevance"], reverse=True)
        
        # If no hits, just return the first few
        if scored_incidents[0]["relevance"] == 0:
            return scored_incidents[:top_n]
            
        return scored_incidents[:top_n]
