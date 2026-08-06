import subprocess
import os

webapp_dir = os.path.join(os.path.dirname(__file__), "webapp")
venv_python = os.path.join(webapp_dir, ".venv", "Scripts", "python.exe")
proc = subprocess.Popen(
    [venv_python, "-m", "reflex", "run", "--frontend-port", "5000", "--backend-port", "5001"],
    cwd=webapp_dir,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    creationflags=subprocess.CREATE_NO_WINDOW,
)
print(f"Reflex PID: {proc.pid}")