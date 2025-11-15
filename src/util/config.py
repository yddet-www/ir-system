from pathlib import Path

CRWL_DIR = Path(__file__).parent.parent / "web-crawler"
CRWL_MAP_FILE = "url_map.jsonl"
CRWL_OUTPUT = CRWL_DIR / "output"
CRWL_HTML = CRWL_OUTPUT / "html"
CRWL_MAP_FP = CRWL_OUTPUT / CRWL_MAP_FILE

INDX_DIR = Path(__file__).parent.parent / "indexer"
INV_IDX_FILE = "inverted_index.json"
INDX_OUTPUT = INDX_DIR / "output"
INV_IDX_FP = INDX_OUTPUT / INV_IDX_FILE

QPROC_DIR = Path(__file__).parent.parent / "processor"
