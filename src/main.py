import subprocess
import webbrowser
import time
import sys

python_path = sys.executable

def run_flask_app():
    subprocess.Popen([python_path, "app.py"])

def open_browser():
    url = "http://localhost:5000"
    webbrowser.open(url)

if __name__ == "__main__":
    run_flask_app()
    time.sleep(2)
    open_browser()
