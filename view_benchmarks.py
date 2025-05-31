import os
import subprocess
import sys
import platform

from setup import get_python_path




def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    
    print("Launching graph viewer...")
    
    command = f'{get_python_path()} -m Utils.graph_viewer -f *.fig -a -s Report'
    
    subprocess.run(command)
    
    sys.exit(0)


if __name__ == "__main__":
    main()