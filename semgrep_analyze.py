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
            f"--text --include '*.css' --include '*.html' --include '*.js'" # Data types to scan/ --text, json, SARIF... this formats can be used too.
        )
        
        # Wsl shell subprocess for semgrep scan
        try:
            result = subprocess.run(
                f"wsl {semgrep_command}",
                shell=True,
                capture_output=True, # For debugging purposes
                text=True,
                encoding="utf-8"
            )
            # Error detection
            if result.returncode != 0:
                print(f"Error: {result.stderr}")
            else:
                print(f"Analysis complete. Output:\n{result.stdout}")
                
        # Returns error
        except subprocess.CalledProcessError as e:
            print(f"Error has occurred while command runs: {e}")
      

                


