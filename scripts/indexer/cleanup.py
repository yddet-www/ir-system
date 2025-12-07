from pathlib import Path
import shutil

script_dir = Path(__file__).parent
output_dir = script_dir.parent.parent / "src" / "indexer" / "output"

if output_dir.exists():
    shutil.rmtree(output_dir)
    print(f"Removed: {output_dir}")
else:
    print(f"Directory doesn't exist: {output_dir}")
