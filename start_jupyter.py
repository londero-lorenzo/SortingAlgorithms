import os
import subprocess
import sys
import platform

from setup import get_python_path

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("Launching jupyter lab, please standby")
    
    command = f'{get_python_path()} -m jupyter lab'
    
    subprocess.run(command)
    
    sys.exit(0)
    

if __name__ == "__main__":
    main()