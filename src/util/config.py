from pathlib import Path

CRWL_DIR = Path(__file__).parent.parent / "web-crawler"
CRWL_OUTPUT = CRWL_DIR / "output"
CRWL_HTML = CRWL_OUTPUT / "html"
CRWL_MAPPING = CRWL_OUTPUT / "url_map.jsonl"

INDX_DIR = Path(__file__).parent / "indexer"

QPROC_DIR = Path(__file__).parent / "processor"
