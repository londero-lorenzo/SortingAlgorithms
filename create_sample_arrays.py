import os
import subprocess
import sys
import platform

from setup import get_python_path


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("Creating arrays...")
    
    command = f'{get_python_path()} -m Utils.ArrayGenerator -f *.json -a -s Array'
    
    subprocess.run(command)
    
    sys.exit(0)


if __name__ == "__main__":
    main()