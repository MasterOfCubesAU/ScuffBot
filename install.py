import os
import argparse
import shutil

VENV_PATH = ".SCUFFBOT"
PYTHON_BIN = "python3.10"

def getBinPath():
    if os.name == "posix":
        return fr"{VENV_PATH}/bin"
    else:
        return f"{VENV_PATH}\Scripts"


def main():
    if args.reinstall or args.clean:
        shutil.rmtree(VENV_PATH)
        if args.clean:
            return
    if not os.path.exists(VENV_PATH):
        if os.name == "posix":
            os.system(f"sudo apt install {PYTHON_BIN}-venv")
        os.system(f"{PYTHON_BIN} -m venv {VENV_PATH}")
    os.system(f"{os.path.join(getBinPath(), 'pip')} install -r requirements.txt")
    if not os.path.exists("logs"):
        os.mkdir("logs")
    print("==================================================================================================")
    print(fr"All dependencies have been installed/updated. To launch SCUFFBOT, execute {os.path.join(getBinPath(), 'python')} launcher.py")
    print("==================================================================================================")

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Install all dependencies for SCUFFBOT.')
    parser.add_argument('--reinstall', action='store_true', help='Force clean install.')
    parser.add_argument('--clean', action='store_true', help='Removes all dependencies.')
    args = parser.parse_args()
    main()
