import subprocess
#import nmap


class NmapScan:
    def __init__(self, output_file, target):
        self.target = target
        self.output_file = output_file
    
    # Basic nmap scan(Host discovery, port scan range: 1-1000, service detection, host status)
    def basic_scan(self):
        print(f"Basic nmap scan started.") 
        command = f"nmap {self.target} -oX {self.output_file}"
        subprocess.run(command, shell=True) # It runs the command in the cmd
        print(f"Basic nmap scan completed.")
     
    # Noisy aggresive scan(Os detection, service version, tracerout, script scanning)
    def aggressive_scan(self):
        print(f"Aggressive nmap scan started.")
        command = f"nmap -A {self.target} -oX {self.output_file}"
        subprocess.run(command, shell=True)

    # Nmap scan for known vulnerabilities
    def vuln_scan(self):
        print(f"Vuln nmap scan started.")
        command = f"nmap --script vuln {self.target} -oX {self.output_file}"
        subprocess.run(command, shell=True)

    # Nmap scan for custom commands    
    def custom_scan(self, custom_options):
        print(f"Custom nmap scan started.")
        command = f"nmap {custom_options} {self.target} -oX {self.output_file}"
        subprocess.run(command, shell=True)


