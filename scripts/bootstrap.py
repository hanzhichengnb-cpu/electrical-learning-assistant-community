#!/usr/bin/env python3
"""Create a task-local PDF runtime. Never installs into the system Python."""
import argparse
from pathlib import Path
import subprocess
import sys
import venv

parser = argparse.ArgumentParser()
parser.add_argument("--runtime", required=True, help="Agent-chosen writable runtime directory")
args = parser.parse_args()
if sys.version_info < (3, 10):
    raise SystemExit("This package needs Python 3.10 or newer.")
root = Path(args.runtime).resolve()
if not (root / "pyvenv.cfg").exists():
    venv.EnvBuilder(with_pip=True).create(root)
python = root / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
requirements = Path(__file__).resolve().parent / "requirements.txt"
try:
    subprocess.run([str(python), "-m", "pip", "install", "--disable-pip-version-check",
                    "--retries", "2", "--timeout", "30", "-r", str(requirements)], check=True)
except subprocess.CalledProcessError:
    raise SystemExit("PDF dependency installation failed; no system packages were changed. "
                     "Keep the partial task and retry only after checking the reported download error.")
print(str(python))
