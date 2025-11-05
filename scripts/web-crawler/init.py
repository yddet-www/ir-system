import subprocess
import sys
from pathlib import Path

script_dir = Path(__file__).parent
crawler_dir = script_dir.parent.parent / "src" / "web-crawler"

cmd = ["scrapy", "crawl", "webcrawler", "-a", "url_file=test_urls.txt"]

result = subprocess.run(
    cmd, cwd=crawler_dir, check=True  # Run from web-crawler directory
)
