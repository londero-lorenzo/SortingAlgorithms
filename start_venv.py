import os
import platform
import subprocess
import sys
from setup import VENV_DIR
from setup import get_activate_path

def open_venv_shell():
    
    activate_path = get_activate_path()
    
    if os.name == 'nt':

        subprocess.run(['cmd.exe', '/k', f'{activate_path} && echo Environment activated. Type \'deactivate\' to exit.'])
    
    else: 

        shell = os.environ.get('SHELL', '/bin/bash')
        command = f'source {activate_path}; echo "Environment activated. Type \'deactivate\' to exit."; exec {shell}'
        subprocess.run([shell, '-c', command])

if __name__ == '__main__':
    open_venv_shell()