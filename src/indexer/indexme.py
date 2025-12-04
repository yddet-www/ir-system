import json
from typing import Any
from src.util.config import CRWL_OUTPUT, INDX_OUTPUT, INV_IDX_FP
from bs4 import BeautifulSoup
from pathlib import Path
import threading
import os
import re
from math import log10
import nltk
from nltk.corpus import stopwords

CPU_COUNT = os.cpu_count() or 1

try:
    STOPWORDS = set(stopwords.words("english"))
except LookupError:
    nltk.download("stopwords")
    STOPWORDS = set(stopwords.words("english"))


class Index:
    def __init__(self, idx_file: str):
        self.index_path: Path = INDX_OUTPUT / idx_file

    def create_index(self, corpus_path):
        if self.index_path.exists():
            raise FileExistsError(
                f"File already exists at {str(self.index_path)}\n     Use load_index() to load file into object instead."
            )

        self.corpus_path: Path = Path(corpus_path)
        self.corpus_mapping: Path = self.corpus_path / "url_map.jsonl"

        # sort so its not so random for my sake
        docs = sorted((self.corpus_path / "html").iterdir())

        self.corpus_size: int = len(docs)

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

        self.inverted_index: dict[str, dict[str, list[int]]] = init_invidx_tfdf(doc_idx)
        Path(INDX_OUTPUT).mkdir(parents=True, exist_ok=True)

        with open(self.index_path, "w") as idx_file:
            idx_obj = {
                "index_path": str(self.index_path),
                "corpus_path": str(self.corpus_path),
                "corpus_mapping": str(self.corpus_mapping),
                "corpus_size": self.corpus_size,
                "inverted_index": self.inverted_index,
            }
            json.dump(idx_obj, idx_file, indent=2)

    def load_index(self):
        if not self.index_path.exists():
            raise FileNotFoundError(
                f"File not found @ {str(self.index_path)}\n Use create_index() to generate a new inverted index file."
            )

        with open(self.index_path, "r") as idx_file:
            idx_obj = json.load(idx_file)

        self.index_path = Path(idx_obj["index_path"])
        self.corpus_path = Path(idx_obj["corpus_path"])
        self.corpus_mapping = Path(idx_obj["corpus_mapping"])
        self.corpus_size = idx_obj["corpus_size"]
        self.inverted_index = idx_obj["inverted_index"]

    def get_idf(self, term: str):
        if term not in self.inverted_index:
            return 0

        n = self.corpus_size
        df = len(self.inverted_index[term])

        idf = log10(n / df)
        return idf

    def get_tf(self, term: str, doc: str):
        return len(self.inverted_index[term][doc])


# Attr:
# https://stackoverflow.com/questions/312443/how-do-i-split-a-list-into-equally-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def tokenizer(html_path: str):
    p = Path(html_path)

    with open(p, "rb") as html:
        soup_obj = BeautifulSoup(html, "html.parser")
        content = soup_obj.get_text(" ", strip=True).lower()

    regex_p = r"[^\w\s]"
    tokens = re.sub(regex_p, "", content).split()
    filtered_tokens = [t for t in tokens if t not in STOPWORDS]

    return filtered_tokens


def ptokenize(html_list: list[Path], doc_idx: dict[str, list[str]]):
    for path in html_list:
        token_list = tokenizer(str(path))
        doc_idx[path.stem] = token_list


def init_invidx_tfdf(doc_idx: dict[str, list[str]]):
    inverted_idx: dict[str, dict[str, list[int]]] = {}

    for doc, term_lst in doc_idx.items():

        # maintain list of positions of term per document
        # note it is always sorted as it assumes list of text is in original ordering
        for pos, term in enumerate(term_lst):
            if term in inverted_idx:
                posting_list = inverted_idx[term].setdefault(doc, [])
                posting_list.append(pos)
            else:
                inverted_idx[term] = {doc: [pos]}

    return inverted_idx


if "__main__" == __name__:
    index_obj = Index("inverted_index.json")

    if not index_obj.index_path.exists():
        print(f"No inverted index found @ {str(INV_IDX_FP)}, creating one...")
        index_obj.create_index(str(CRWL_OUTPUT))

    else:
        index_obj.load_index()

    print(index_obj.get_idf("digimon"))

    for doc in index_obj.inverted_index["digimon"].keys():
        curr_tf = index_obj.get_tf("digimon", doc)
        print(f"{doc}: {curr_tf}")

    exit(0)
