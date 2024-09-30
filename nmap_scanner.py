import subprocess
import nmap


class NmapScan:
    def __init__(self, directory, output_file, target):
        self.target = target
        self.directory = directory
        self.output_file = output_file
        
    def basic_scan(self):
        print(f"Basic nmap scan started.")
        command = f"nmap {self.target} -oX {self.output_file}"
        subprocess.run(command, shell=True)
        print(f"Basic nmap scan completed.")
        





