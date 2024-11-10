import subprocess


class ZapScan:
    def __init__(self, target, output_file, zap_dir):
        self.target = target # target url
        self.output_file = output_file # output file
        self.zap_dir = zap_dir # zap install directory
        
    def quick_scan(self):
        print(f"Quick scan started!")
        command = f"cd {self.zap_dir} && zap.bat -cmd -quickurl {self.target} -quickout {self.output_file}"

        process = subprocess.run(command, shell=True) # Runs the command in cmd

    def full_scan(self):
        print(f"Full scan started!")
        command = f"cd {self.zap_dir} && zap.bat -cmd -quickurl {self.target} -quickout {self.output_file}"

        process = subprocess.run(command, shell=True) # Runs the command in cmd




