import os
import subprocess
import sys
import platform

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    if os.name == 'nt':
        activate = os.path.join(script_dir, ".labProjVenv", "Scripts", "activate.bat")
        command = f'cmd.exe /c "{activate} && echo Launching jupyter lab, please standby && jupyter lab"'
        subprocess.run(command, shell=True)
    else:
        activate = os.path.join(script_dir, ".labProjVenv", "bin", "activate")
        command = f'bash -c "source {activate}&& echo "Launching jupyter lab, please standby" && jupyter lab"'
        subprocess.run(command, shell=True)

if __name__ == "__main__":
    main()