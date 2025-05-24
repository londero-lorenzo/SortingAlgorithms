import os
import platform
import subprocess
import glob
import sys
import time

from setup import VENV_DIR
from setup import get_jupyter_path
        
def clear_outputs_notebooks():
    choice = input("Notebook cleaning tool.\nAll notebooks will be clean, proceed? [Y/n]\n")
    if choice != 'Y':
        print("Cleaning aborted.")
        time.sleep(0.5)
        sys.exit(1)
    jupyter_path = get_jupyter_path()
    if not os.path.isfile(jupyter_path):
        print(f"Error: {jupyter_path} not found.")
        sys.exit(1)
    
    notebooks = glob.glob("**/*.ipynb", recursive= True)
    print(f"Found {len(notebooks)} notebooks.")
    for nb in notebooks:
        print(f"Cleaning output cells from notebook: {nb}")
        result = subprocess.run([jupyter_path, 'nbconvert', '--clear-output', '--inplace', nb])
        if result.returncode != 0:
            print(f"Exception raised while cleaning notebook: {nb}")
            
if __name__ == '__main__':
    clear_outputs_notebooks()