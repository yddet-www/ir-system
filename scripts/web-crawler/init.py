import subprocess
from pathlib import Path

script_dir = Path(__file__).parent
crawler_dir = script_dir.parent.parent / "src" / "web-crawler"

cmd = [
    "scrapy",
    "crawl",
    "webcrawler",
    "-a",
    "url_file=urls.txt",
    # "-a",
    # "output_path=output/digimon",
]

result = subprocess.run(
    cmd, cwd=crawler_dir, check=True  # Run from web-crawler directory
)
