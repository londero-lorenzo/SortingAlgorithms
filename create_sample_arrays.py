import os
import subprocess
import sys
import platform

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    if os.name == 'nt':
        scripts_folder = os.path.join(script_dir, ".labProjVenv", "Scripts")
        activate = os.path.join(scripts_folder, "activate.bat")
        python = os.path.join(scripts_folder, "python.exe")
        
        command = f'cmd.exe /k "{activate} && echo Environment activated.&& echo Creating arrays... && {python} -m Utils.ArrayGenerator -f *.json -a -s Array && pause && exit"'
        subprocess.run(command, shell=True)
    else:
        activate = os.path.join(venv_dir, "bin", "activate")
        python = os.path.join(venv_dir, "bin", "python")

        command = f'/bin/bash -c "source {activate} && echo Environment activated. && echo Creating arrays... && {python} -m Utils.ArrayGenerator -f *.json -a -s Array; read"'
        subprocess.run(['bash', '-c', shell_cmd])


if __name__ == "__main__":
    main()