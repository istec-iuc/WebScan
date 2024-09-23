import os
import subprocess

#[D:asyncio] Using proactor: %s
#Exception in thread Thread-7:
#Traceback (most recent call last):
#  File "C:\Users\erngu\AppData\Local\Programs\Python\Python39\lib\threading.py", line 980, in _bootstrap_inner
#    self.run()
#  File "C:\Users\erngu\AppData\Local\Programs\Python\Python39\lib\threading.py", line 917, in run
#    self._target(*self._args, **self._kwargs)
#  File "C:\Users\erngu\AppData\Local\Programs\Python\Python39\lib\subprocess.py", line 1479, in _readerthread
#    buffer.append(fh.read())
#  File "C:\Users\erngu\AppData\Local\Programs\Python\Python39\lib\encodings\cp1254.py", line 23, in decode
#    return codecs.charmap_decode(input,self.errors,decoding_table)[0]
#UnicodeDecodeError: 'charmap' codec can't decode byte 0x90 in position 76: character maps to <undefined>


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
                
        except subprocess.CalledProcessError as e:
            print(f"Error has occurred while command runs: {e}")

