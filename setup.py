import os
import sys
import subprocess
import venv
import platform

VENV_DIR = ".labProjVenv"
REQUIREMENTS_FILE = "requirements.txt"


SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
VENV_DIR = os.path.join(SCRIPT_DIR, VENV_DIR)
REQUIREMENTS_FILE = os.path.join(SCRIPT_DIR, REQUIREMENTS_FILE)

def create_virtualenv():
    print("Creating virtual environment...")
    builder = venv.EnvBuilder(with_pip=True)
    builder.create(VENV_DIR)
    
def get_pip_path():
    if os.name == 'nt':
        return os.path.join(VENV_DIR, "Scripts", "pip.exe")
    else:
        return os.path.join(VENV_DIR, "bin", "pip")

def get_jupyter_path():
    if os.name == 'nt':
        return os.path.join(VENV_DIR, "Scripts", "jupyter.exe")
    else:
        return os.path.join(VENV_DIR, "bin", "jupyter")
        
        
def get_activate_path():
    if os.name == 'nt':
        return os.path.join(VENV_DIR, 'Scripts', 'activate.bat')
    else:
        return os.path.join(VENV_DIR, 'bin', 'activate')
    
    
def get_python_path():
    if os.name == 'nt':
        return os.path.join(VENV_DIR, 'Scripts', 'python.exe')
    else:
        return os.path.join(VENV_DIR, 'bin', 'python')

def install_requirements():
    pip_path = get_pip_path()

    if not os.path.isfile(REQUIREMENTS_FILE):
        print(f"Error: {REQUIREMENTS_FILE} not found in {SCRIPT_DIR}")
        sys.exit(1)

    print("Installing packages from requirements.txt...")
    subprocess.check_call([pip_path, "install", "-r", REQUIREMENTS_FILE])
   

def install_filters():
    print("Installing git filters...")
    activate_path = get_activate_path()
    if not os.path.isfile(activate_path):
        print(f"ERROR: activation executable not found at {activate_path}")
        sys.exit(1)


    if os.name == 'nt':
        clean_command = f'cmd.exe /c "{activate_path} && python {os.path.abspath("strip_notebook_filter.py")}"'

        subprocess.check_call([
        "git", "config", "filter.strip-notebook.clean",
        clean_command
        ])
        
    else:
    
        clean_command = f'bash -c "source {activate_path} && jupyter  nbconvert --ClearOutputPreprocessor.enabled=True --ClearMetadataPreprocessor.enabled=True --to notebook --stdout"'
        subprocess.check_call([
        "git", "config", "filter.strip-notebook.clean",
        clean_command
        ])
    subprocess.check_call(["git", "config", "filter.strip-notebook.smudge", 'cat'])
        
    
    
def main():
    if os.path.isdir(VENV_DIR):
        print(f"Virtual environment already exists in {VENV_DIR}")
    else:
        create_virtualenv()
    install_requirements()
    install_filters()
    print("Setup completed.")
    print(f"To activate the environment manually:\n")

    if os.name == 'nt':
        print(f" {VENV_DIR}\\Scripts\\activate.bat")
    else:
        print(f" source {VENV_DIR}/bin/activate")
    
    print()
    input("Press ENTER to quit.")

if __name__ == "__main__":
    main()