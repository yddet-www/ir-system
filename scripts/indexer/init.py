import sys
import subprocess
from pathlib import Path

script_dir = Path(__file__).parent.parent.parent

cmd = [
    sys.executable,
    "-m",
    "src.indexer.indexme",
]

result = subprocess.run(
    cmd, cwd=script_dir, check=True  # Run from web-crawler directory
)
