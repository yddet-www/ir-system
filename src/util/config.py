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

SRCH_DIR = Path(__file__).parent.parent / "search"
SRCH_QUERY_FILE = "query_map.csv"
SRCH_LOGS = SRCH_DIR / "logs"
SRCH_LOGS_FP = SRCH_LOGS / SRCH_QUERY_FILE


QPROC_DIR = Path(__file__).parent.parent / "processor"
