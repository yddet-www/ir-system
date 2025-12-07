import subprocess
from pathlib import Path
import sys

script_dir = Path(__file__).parent
crawler_dir = script_dir.parent.parent / "src" / "web-crawler"

cmd = [sys.executable, "-m", "scrapy", "crawl", "webcrawler", "-a", "url_file=urls.txt"]

result = subprocess.run(
    cmd, cwd=crawler_dir, check=True  # Run from web-crawler directory
)
