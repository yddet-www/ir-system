import subprocess
from pathlib import Path
import sys

script_dir = Path(__file__).parent
root_dir = script_dir.parent

cmd = [sys.executable, "-m", "flask", "--app", "src/search", "run", "--debug"]

result = subprocess.run(
    cmd, cwd=root_dir, check=True  # Run from web-crawler directory
)
