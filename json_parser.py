import json

class jsonParser:
    def __init__(self, json_data):
        self.json_data = json_data
        
    
    def parse_security_results(self):
        
        results = self.json_data.get("results", [])
        parsed_results = []
        
        for result in results:
            check_id = result.get("check_id", "Unknown Check ID")
            # Add more
            
            parsed_results.append({
                "check_id": check_id
                # Add more
                })
        return parsed_results
    
    def print_report(self, parsed_results):
        # Generates a simple report from parsed results (Simple for now (:< )
        for idx, result in enumerate(parsed_results):
            print(f"Security Issue {idx + 1}:")
            print(f"Check ID: {result['check_id']}")



