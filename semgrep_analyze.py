import os
import subprocess
import json

# scan_results.json format this file!!

class SemgrepAnalyzer:
    def __init__(self, directory, output_file):
        self.directory = directory
        self.output_file = output_file
        
    def analyze(self):
        semgrep_command = (
            f"/home/quarius/.local/bin/semgrep scan {self.directory} " # Semgreps location in wsl and directory for scan
            f"--output {self.output_file} " # Output file's directory
            f"--json --include '*.css' --include '*.html' --include '*.js'" # Data types to scan
        )
        
        # Wsl shell subprocess for semgrep scan
        try:
            result = subprocess.run(
                f"wsl {semgrep_command}",
                shell=True,
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            
            if result.returncode != 0:
                print(f"Error: {result.stderr}")
            else:
                print(f"Analysis complete. Output:\n{result.stdout}")
                
                # self.format_json_file()
  
        except subprocess.CalledProcessError as e:
            print(f"Error has occurred while command runs: {e}")

    # def format_json_file(self):
    #     try:
    #         with open(self.output_file, 'r', encoding='utf-8') as file:
    #             data = json.load(file)
            
    #         with open(self.output_file, 'w', encoding='utf-8') as file:
    #             json.dump(data, file, indent=4)
                
    #         print(f"JSON output formatted successfully in {self.output_file}")

    #     except Exception as e:
    #         print(f"Error occurred during formatting JSON file: {e}")                

                


