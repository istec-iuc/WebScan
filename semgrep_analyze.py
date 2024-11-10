import os
import subprocess
import json

# scan_results.json if you take outputs as json then use pretty json function.

class SemgrepAnalyzer:
    def __init__(self, directory, output_file):
        self.directory = directory
        self.output_file = output_file
        
    def analyze(self):
        command = (
            f"/root/.local/bin/semgrep scan {self.directory} " # Semgreps location in wsl and directory for scan
            f"--output {self.output_file} " # Output file's directory
            f"--json --include '*.css' --include '*.html' --include '*.js'" # Data types to scan/ --text, json, SARIF... these formats can be used too.
        )
        
        # Wsl shell subprocess for semgrep scan
        try:
            result = subprocess.run(
                f"wsl {command}",
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
      

                


