import sys
import subprocess
import os

MIN_PYTHON = (3, 8)


def check_python():
    if sys.version_info < MIN_PYTHON:
        print(f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} or higher is required.")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"Python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")


def install_deps():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        print("Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", req_path])


def run_app():
    main_path = os.path.join(os.path.dirname(__file__), "main.py")
    subprocess.check_call([sys.executable, main_path])


if __name__ == "__main__":
    check_python()
    install_deps()
    run_app()
