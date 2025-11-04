from pathlib import Path
import shutil

script_dir = Path(__file__).parent
html_dir = script_dir.parent.parent / "src" / "web-crawler" / "output" / "html"

if html_dir.exists():
    shutil.rmtree(html_dir)
    print(f"Removed: {html_dir}")
else:
    print(f"Directory doesn't exist: {html_dir}")
