import subprocess
import os


class SQLScan:
    def __init__(self, target, output_file, sqlmap_dir):
        self.target = target
        self.output_file = output_file
        self.sqlmap_dir = sqlmap_dir # sqlmap.py's directory for example C:/Users/asd/AppData/Local/Programs/sqlmap/ dont forget the last "/"
        
    def quick_sqlmap(self, additional_options=None):
        print(f"Quick SQLMAP started!")
        command = (
            f"python {os.path.join(self.sqlmap_dir, 'sqlmap.py')} -u {self.target} "
            f"-v 1 --batch --output-dir={os.path.dirname(self.output_file)}"
        )
        
        if additional_options:
            command += f" {additional_options}"
            # Additional options can be added such as " --dbs, --tables, --colums, --dump, --level=(1 to 5), --risk=(1 to 3) 
        process = subprocess.run(command, shell=True)
        
        
    def full_sqlmap(self, additional_options=None):
        print(f"Full SQLMAP started!")
        command = (
            f"python {os.path.join(self.sqlmap_dir, 'sqlmap.py')} -u {self.target} -v 1 --batch "
            f"--dbs --tables --columns --dump --level=5 --risk=3 --output-dir={os.path.dirname(self.output_file)}"
        print(f"Full SQLMAP completed!")
        )
    




