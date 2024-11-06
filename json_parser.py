import json
import os
from unittest import result

class JSONParser:
    def __init__(self, json_data):
        self.json_data = json_data


class ZAPParser(JSONParser):
    def parse_zap_report(self, zap_json_data):
        self.zap_json_data = zap_json_data

        zap_report = []
        for site in self.zap_json_data.get("site", []):
            site_info = {
                "name": site.get("@name"),
                "host": site.get("@host"),
                "port": site.get("@port"),
                "ssl": site.get("@ssl"),
                "alerts": []
                }
            # Parse each alert within the site
            for alert in site.get("alerts", []):
                alert_info = {
                    "pluginid": alert.get("pluginid"),
                    "alertRef": alert.get("alertRef"),
                    "name": alert.get("name"),
                    "riskcode": alert.get("riskcode"),
                    "confidence": alert.get("confidence"),
                    "riskdesc": alert.get("riskdesc"),
                    "desc": alert.get("desc"),
                    "count": alert.get("count"),
                    "solution": alert.get("solution"),
                    "otherinfo": alert.get("otherinfo"),
                    "reference": alert.get("reference"),
                    "cweid": alert.get("cweid"),
                    "wascid": alert.get("wascid"),
                    "sourceid": alert.get("sourceid"),
                    "instances": []
                }
            
                # Parse each instance within the alert
                for instance in alert.get("instances", []):
                    instance_info = {
                        "uri": instance.get("uri"),
                        "method": instance.get("method"),
                        "param": instance.get("param"),
                        "attack": instance.get("attack"),
                        "evidence": instance.get("evidence"),
                        "otherinfo": instance.get("otherinfo")
                    }
                    alert_info["instances"].append(instance_info)
            
                site_info["alerts"].append(alert_info)
        
            zap_report.append(site_info)
        return zap_report

    def update_tex_report(self, zap_report, latex_file_path):
        # Read the LaTex file
        with open(latex_file_path, "r") as file:
            latex_content = file.read()
    

        # ---Risk Summary---
        # Risk count dictionary
        zap_impact_count = {
            "LOW": 0,
            "MEDIUM": 0,
            "HIGH": 0,
            "CRITICAL": 0
        }

        # Loop through each site in zap_report
        for site in zap_report:
            for alert in site.get("alerts", []):
                riskcode = alert.get("riskcode", "")
                instances = alert.get("instances", [])
                count = int(alert.get("count", 0))  # Convert count to integer

                # Update the counts based on risk code and instances
                if riskcode == "1":  
                    zap_impact_count["LOW"] += count
                elif riskcode == "2":  
                    zap_impact_count["MEDIUM"] += count
                elif riskcode == "3": 
                    zap_impact_count["HIGH"] += count
                elif riskcode == "4": 
                    zap_impact_count["CRITICAL"] += count

        # Replace zap risk placeholders with actual counts
        latex_content = latex_content.replace("zaplc", str(zap_impact_count["LOW"]))
        latex_content = latex_content.replace("zapmc", str(zap_impact_count["MEDIUM"]))
        latex_content = latex_content.replace("zaphc", str(zap_impact_count["HIGH"]))
        latex_content = latex_content.replace("zapcc", str(zap_impact_count["CRITICAL"]))

        # ---Risk Summary---

        # ---Vulnerability Categories---
        zap_category_counts = {}

        for site in zap_report:
            for alert in site.get("alerts", []):  
                category_name = alert.get("name")  
                count = int(alert.get("count", 0))
                if category_name:  # Check if the name exists
                    if category_name in zap_category_counts:
                        zap_category_counts[category_name] += count
                    else:
                        zap_category_counts[category_name] = count  # Initialize count

        # Create LaTeX formatted list items for the categories with counts
        category_items = ""
        for i, (category, count) in enumerate(zap_category_counts.items(), start=1):
            category_items += f"\\item Category {i}: {category} | {count}\n"

        # Replace the placeholder with actual category list items
        latex_content = latex_content.replace("\\item ZapCategories:", category_items)

        # ---Vulnerability Categories---

        # --Vulnerability by Page---

        # Initialize a LaTeX formatted items string for vulnerabilities
        zap_vuln_items = ""

        # Loop through each site in the parsed report
        for site_idx, site in enumerate(zap_report, 1):
            site_name = site.get("name", "Unknown Site")
            host = site.get("host", "N/A")
            port = site.get("port", "N/A")
            ssl = site.get("ssl", "N/A")

            host = (
                host.replace("{", "\\{")
                    .replace("}", "\\}")
                    .replace("%", "\\%")
                )

            # Add site information as a section in latex
            zap_vuln_items += (
                f"\\section*{{Site {site_idx}: {site_name}}}\n"
                f"Host: {host}, Port: {port}, SSL: {ssl}\n\n"
            )

            # Loop through each alert within the site
            for alert_idx, alert in enumerate(site["alerts"], 1):
                alert_name = alert.get("name", "N/A")
                risk_desc = alert.get("riskdesc", "N/A")
                description = alert.get("desc", "N/A")

                # Escape LaTeX special characters in the description
                description = (
                    description.replace("\u2014", "---")
                               .replace("{", "\\{")
                               .replace("}", "\\}")
                               .replace("%", "\\%")
                               .replace("&", "\\&")
                               .replace("#", "\\#")
                               .replace("<p>", "") 
                               .replace("</p>", "")
                )

                # Builds the table for each vulnerability
                zap_vuln_items += (
                    "\\begin{center}\n"
                    "\\renewcommand{\\arraystretch}{1.3}\n"
                    "\\begin{longtable}{|l|p{10cm}|}\n"
                    "\\hline\n"
                    f"\\multicolumn{{2}}{{|c|}}{{\\textbf{{Vulnerability {alert_idx}}}}} \\\\\n"
                    "\\hline\n"
                    f"\\textbf{{Risk Level}} & {risk_desc} \\\\\n"
                    "\\hline\n"
                    f"\\textbf{{Vulnerability Name}} & {alert_name} \\\\\n"
                    "\\hline\n"
                    f"\\textbf{{Description}} & {description} \\\\\n"
                    "\\hline\n"
                )

                # Add instances
                instances = alert.get("instances", [])
                if instances:
                    zap_vuln_items += "\\textbf{Instances} & \\textbf{URI} \\\\\n"
                    zap_vuln_items += "\\hline\n"
                    for idx, instance in enumerate(instances, start=1):
                        uri = instance.get("uri", "N/A")
                        # Escape special characters in URI
                        uri = (
                            uri.replace("{", "\\{")
                               .replace("}", "\\}")
                               .replace("%", "\\%")
                               .replace("&", "\\&")
                               .replace("#", "\\#")
                               .replace("_", "\\_")
                               .replace("`", "\\`")
                               .replace("\\x3c", "")  
                               .replace("\\x3e", "")  
                        )
                        # Add instance number and URI to table
                        zap_vuln_items += f"Instance {idx} & \\url{{{uri}}} \\\\\n"
                        zap_vuln_items += "\\hline\n"

                # Close the table
                zap_vuln_items += (
                    "\\end{longtable}\n"
                    "\\end{center}"
                    "\\vspace{0.7cm}\n"
                )

        # Replace placeholder in LaTeX content with the generated vulnerability items
        latex_content = latex_content.replace("%ZapVulnerabilities by Page:", zap_vuln_items)

        # --Vulnerability by Page---


        # Write the updated LaTeX content back to the file
        with open(latex_file_path, "w") as file:
            file.write(latex_content)

        print(f"Updated LaTeX file at {latex_file_path} Dynamic Analysis.")
            

class SemgrepParser(JSONParser):
    def parse_report(self):
        report = []
        for result in self.json_data["results"]:
            # Extract relevant information for each result
            parsed_result = {
                #"check_id": result.get("check_id"),
                "path": result.get("path"),
                "start": result.get("start", {}).get("line", "N/A"),
                "start_col": result.get("start", {}).get("col", "N/A"),
                "end": result.get("end", {}).get("line", "N/A"),
                "end_col": result.get("end", {}).get("col", "N/A"),
                "message": result["extra"].get("message", ""),
                "confidence": result["extra"]["metadata"].get("confidence"),
                "impact": result["extra"]["metadata"].get("impact"),
                #"cwe": result["extra"]["metadata"].get("cwe", []),
                #"owasp": result["extra"]["metadata"].get("owasp", []),
                #"references": result["extra"]["metadata"].get("references", []),
                #"technology": result["extra"]["metadata"].get("technology", []),
                "vulnerability_class": result["extra"]["metadata"].get("vulnerability_class", []),
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
    
    def update_latex_with_category(self, parsed_report, latex_file_path):
        # Collect categories and their counts from the parsed report
        category_counts = {}
        for result in parsed_report:
            if result.get("vulnerability_class"):
                for category in result["vulnerability_class"]:
                    if category in category_counts:
                        category_counts[category] += 1
                    else:
                        category_counts[category] = 1

        with open(latex_file_path, "r") as file:
            latex_content = file.read()

        # Create LaTeX formatted list items for the categories with counts
        category_items = ""
        for i, (category, count) in enumerate(category_counts.items(), start=1):
            category_items += f"\\item Category {i}: {category} | {count}\n"

        # Replace the placeholder with actual category list items
        latex_content = latex_content.replace("\item Categories:", category_items)

        # Write the updated LaTeX content back to the file
        with open(latex_file_path, "w") as file:
            file.write(latex_content)

        print(f"Updated LaTeX file at {latex_file_path} with category items.")

    def update_vuln_by_page(self, parsed_report, latex_file_path):
        # Read the LaTeX file
        with open(latex_file_path, "r") as file:
            latex_content = file.read()

        # Create LaTeX formatted items for vulnerabilities
        vuln_items = ""
        for idx, vulnerability in enumerate(parsed_report, 1):
            path = vulnerability.get("path", "N/A")

            # Condition that provides path splitting
            if "ScrapedFiles" in path:
                path = path.split("ScrapedFiles", 1)[-1] # Gets the string after "ScrapedFiles"
                path = "ScrapedFiles" + path


            vuln_class = vulnerability.get("vulnerability_class", "N/A")
            end_line = vulnerability.get("start", "N/A") # end is start \ start is end !!!
            end_col = vulnerability.get("start_col", "N/A")
            start_line = vulnerability.get("end", "N/A")
            start_col = vulnerability.get("end_col", "N/A")
            message = vulnerability.get("message", "N/A")

            # Escape LaTeX special characters in the message
            message = (
                message.replace("{", "\\{")
                       .replace("}", "\\}")
                       .replace("\\url", "\\\\url")
                       .replace("�", "?")
                       .replace("%", "\\%")
            )
            # Construct LaTeX formatted items with a table
            vuln_items += (
                "\\begin{table}[!h]\n"
                "\\centering\n"
                "\\renewcommand{\\arraystretch}{1.3}\n"
                "\\begin{tabular}{|l|p{10cm}|}\n"
                "\\hline\n"
                f"\\multicolumn{{2}}{{|c|}}{{\\textbf{{Vulnerability {idx}}}}} \\\\\n"
                "\\hline\n"
                f"\\multicolumn{{2}}{{|l|}}{{\\textbf{{Path}}: {path}}} \\\\\n"
                "\\hline\n"
                f"\\textbf{{Vulnerability Class}} & {vuln_class} \\\\\n"
                "\\hline\n"
                f"\\textbf{{Start}} & line: {end_line} \\quad col: {end_col} \\\\\n"
                "\\hline\n"
                f"\\textbf{{End}} & line: {start_line} \\quad col: {start_col} \\\\\n"
                "\\hline\n"
                f"\\textbf{{Message}} & {message} \\\\\n"
                "\\hline\n"
                "\\end{tabular}\n"
                "\\end{table}\n"
                "\\vspace{0.7cm}\n"  # Adds some space between each vulnerability
                "\\FloatBarrier\n"                
            )

        # Replace the placeholder with actual vulnerability items
        latex_content = latex_content.replace("%Vulnerabilities by Page:", vuln_items)

        # Write the updated LaTeX content back to the file
        with open(latex_file_path, "w") as file:
            file.write(latex_content)

        print(f"Updated LaTeX file at {latex_file_path} with vulnerability items.")


