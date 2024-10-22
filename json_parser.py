import json

class JSONParser:
    def __init__(self, json_data):
        self.json_data = json_data

class ZAPParser(JSONParser):
    def parse_report(self):
        report = []
        for site in self.json_data['site']:
            site_info = {
                "name": site["@name"],
                "host": site["@host"],
                "port": site["@port"],
                "ssl": site["@ssl"],
                "alerts": []
            }

            for alert in site["alerts"]:
                alert_info = {
                    "alertRef": alert["alertRef"],
                    "name": alert["name"],
                    "riskcode": alert["riskcode"],
                    "confidence": alert["confidence"],
                    "riskdesc": alert["riskdesc"],
                    "desc": alert["desc"],
                    "instances": alert.get("instances", [])
                }
                site_info["alerts"].append(alert_info)

            report.append(site_info)
        return report

    def print_report(self, report):
        for site in report:
            print(f"Site: {site['name']}")
            for alert in site['alerts']:
                print(f"\n  Alert: {alert['name']}, Risk: {alert['riskdesc']}")
                print(f"  Description: {alert['desc']}")
                if alert['instances']:
                    print(f"\nInstances:")
                    for instance in alert["instances"]:
                        print(f"\n  URI: {instance['uri']}")
                        print(f"    Method: {instance['method']}")
                        print(f"    Evidence: {instance['evidence']}")
                        print(f"    Other Info: {instance['otherinfo']}")

    def save_report_to_file(self, report, file_path):
        with open(file_path, "w") as file:
            for site in report:
                file.write(f"\nSite: {site['name']}\n")
                for alert in site['alerts']:
                    file.write(f"\nAlert: {alert['name']}, Risk: {alert['riskdesc']}, Confidence: {alert['confidence']}\n")
                    file.write(f"Description: {alert['desc']}\n")
                    if alert['instances']:
                        file.write(f"Instances:\n")
                        for instance in alert["instances"]:
                            file.write(f"\n  URI: {instance['uri']}\n\n")
                            if "method" in instance and instance["method"]:
                                file.write(f"  Method: {instance['method']}\n")
                            if "evidence" in instance and instance["evidence"]:
                                file.write(f"  Evidence: {instance['evidence']}\n")
                            if "otherinfo" in instance and instance["otherinfo"]:
                                file.write(f"  Other Info: {instance['otherinfo']}\n")

    def save_br_to_file(self, report, br_file_path):
        with open(br_file_path, "w") as file:
            for site in report:
                file.write(f"\nSite: {site['name']}\n")
                for alert in site['alerts']:
                    file.write(f"\n  Alert: {alert['name']}, Risk: {alert['riskdesc']}, Confidence: {alert['confidence']}\n")
                    file.write(f"  Description: {alert['desc']}\n")

class SemgrepParser(JSONParser):
    def parse_report(self):
        report = []
        for result in self.json_data['results']:
            # Extract relevant information for each result
            parsed_result = {
                #"check_id": result.get("check_id"),
                #"path": result.get("path"),
                #"start_line": result["start"]["line"],
                #"start_col": result["start"]["col"],
                #"end_line": result["end"]["line"],
                #"end_col": result["end"]["col"],
                #"message": result["extra"].get("message", ""),
                "confidence": result["extra"]["metadata"].get("confidence"),
                "impact": result["extra"]["metadata"].get("impact"),
                #"cwe": result["extra"]["metadata"].get("cwe", []),
                #"owasp": result["extra"]["metadata"].get("owasp", []),
                #"references": result["extra"]["metadata"].get("references", []),
                #"technology": result["extra"]["metadata"].get("technology", []),
                #"vulnerability_class": result["extra"]["metadata"].get("vulnerability_class", []),
                #"taint_source": result["extra"]["dataflow_trace"].get("taint_source", []),
                #"taint_sink": result["extra"]["dataflow_trace"].get("taint_sink", []),
            }
            report.append(parsed_result)
        return report
        
    def risk_counter(self, report):
        # Count occurrences of different impact levels
        impact_count = {
            "LOW": 0,
            "MEDIUM": 0,
            "HIGH": 0,
            "CRITICAL": 0
        }

        for result in report:
            impact = result.get("impact", "LOW")  # Default to "LOW" if impact is not specified
            if impact in impact_count:
                impact_count[impact] += 1
                print(f"{impact_count},{impact_count[impact]},{impact_count['LOW']}")

        return impact_count
            
    def update_latex_with_risks(self, impact_count, latex_file_path):
        # Read the LaTeX file
        with open(latex_file_path, "r") as file:
            latex_content = file.read()

        # Replace placeholders with actual counts
        latex_content = latex_content.replace("lowcount", str(impact_count["LOW"]))
        latex_content = latex_content.replace("mediumcount", str(impact_count["MEDIUM"]))
        latex_content = latex_content.replace("highcount", str(impact_count["HIGH"]))
        latex_content = latex_content.replace("criticalcount", str(impact_count["CRITICAL"]))

        # Write the updated LaTeX content back to the file
        with open(latex_file_path, "w") as file:
            file.write(latex_content)

        print(f"Updated LaTeX file at {latex_file_path} with risk counts.")
