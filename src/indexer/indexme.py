from src.util.config import CRWL_MAPPING, CRWL_OUTPUT, CRWL_HTML
from bs4 import BeautifulSoup
from pathlib import Path
import threading, os, re

CPU_COUNT = os.cpu_count() or 8


def tokenizer(html_path: str):
    p = Path(html_path)

    with open(p, "rb") as html:
        soup_obj = BeautifulSoup(html, "html.parser")
        content = soup_obj.get_text(" ", strip=True).lower()

    regex_p = r"[^\w\s]"
    tokens = re.sub(regex_p, "", content).split()

    return tokens


def ptokenize(html_list: list[Path], doc_idx: dict[str, list[str]]):
    for path in html_list:
        token_list = tokenizer(str(path))
        doc_idx[path.name] = token_list


# Attr:
# https://stackoverflow.com/questions/312443/how-do-i-split-a-list-into-equally-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


if "__main__" == __name__:
    path = CRWL_HTML

    docs = [file for file in path.iterdir()]
    chunk_size = len(docs) // CPU_COUNT
    document_chunks = chunks(docs, chunk_size)

    threads = []
    doc_idx: dict[str, list[str]] = {}
    for chunk in document_chunks:
        t = threading.Thread(target=ptokenize, args=(chunk, doc_idx))
        threads.append(t)

    for t in threads:
        t.start()

    for t in threads:
        t.join()

    print(doc_idx)

    exit(0)
