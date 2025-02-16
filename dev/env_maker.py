import os
import subprocess

def setup_virtual_environment():
    # Create virtual environment
    subprocess.check_call([os.sys.executable, '-m', 'venv', 'env'])
    # Activate virtual environment
    activate_script = os.path.join('env', 'bin', 'activate')
    if os.name == 'posix':
        activate_script = os.path.join('env', 'bin', 'activate')
    print(f"Run the following command to activate the virtual environment:\nsource {activate_script}")

if __name__ == "__main__":
    setup_virtual_environment()
