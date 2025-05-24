import os
import platform
import subprocess
import sys
from setup import VENV_DIR

def open_venv_shell(venv_path='.labProjVenv'):
    system = platform.system()

    if system == 'Windows':
        activate_path = os.path.join(venv_path, 'Scripts', 'activate.bat')
        
        subprocess.run(['cmd.exe', '/k', f'{activate_path} && echo Environment activated. Type \'deactivate\' to exit.'])
    
    elif system in ['Linux', 'Darwin']: 
        activate_path = os.path.join(venv_path, 'bin', 'activate')
        
        shell = os.environ.get('SHELL', '/bin/bash')
        command = f'source {activate_path}; echo "Environment activated. Type \'deactivate\' to exit."; exec {shell}'
        subprocess.run([shell, '-c', command])

    else:
        print(f"{system} operating system not supported.")

if __name__ == '__main__':
    open_venv_shell(VENV_DIR)