import json

class ZAPReportParser:
    def __init__(self, json_data):
        self.json_data = json_data

    def parse_report(self):
        report = []
        for site in self.json_data['site']:
            # Extract site information
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
