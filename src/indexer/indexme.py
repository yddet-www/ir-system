import json
from src.util.config import CRWL_OUTPUT, INDX_OUTPUT, INV_IDX_FILE
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
    def __init__(
        self, idx_file: Path = Path(INV_IDX_FILE), corpus_path: Path = CRWL_OUTPUT
    ):
        self.index_path: Path = INDX_OUTPUT / idx_file
        self._magnitude_cache = {}  # inshallah this speeds up cosine search

        if not self.index_path.exists():
            print(f"No inverted index found @ {self.index_path}, creating one...")
            self.create_index(corpus_path)
        else:
            self.load_index()

    def create_index(self, corpus_path: Path):
        if self.index_path.exists():
            raise FileExistsError(
                f"File already exists at {str(self.index_path)}\n     Use load_index() to load file into object instead."
            )

        self.corpus_path: Path = corpus_path
        self.corpus_mapping: Path = self.corpus_path / "url_map.jsonl"

        # run the crawler first, moron
        if not self.corpus_mapping.exists():
            raise FileNotFoundError(
                f'Expected a "url_map.jsonl" file at @ {self.corpus_mapping}, found none'
            )

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
        self.bigram_index: dict[str, list[str]] = init_bigram_idx(
            list(self.inverted_index.keys())
        )
        Path(INDX_OUTPUT).mkdir(parents=True, exist_ok=True)

        with open(self.index_path, "w") as idx_file:
            idx_obj = {
                "index_path": str(self.index_path),
                "corpus_path": str(self.corpus_path),
                "corpus_mapping": str(self.corpus_mapping),
                "corpus_size": self.corpus_size,
                "inverted_index": self.inverted_index,
                "bigram_index": self.bigram_index,
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
        self.bigram_index = idx_obj["bigram_index"]

    def get_idf(self, term: str):
        if term not in self.inverted_index:
            return 0

        n = self.corpus_size
        df = len(self.inverted_index[term])

        idf = log10(n / df)
        return idf

    def get_tf(self, term: str, doc: str):
        if term not in self.inverted_index:
            return 0

        return len(self.inverted_index[term][doc])

    def _get_doc_magnitude(self, doc_id: str):
        if doc_id in self._magnitude_cache:
            return self._magnitude_cache[doc_id]

        magnitude_squared = 0

        # for every term in this document
        for term in self.inverted_index:
            if doc_id in self.inverted_index[term]:
                tf = self.get_tf(term, doc_id)
                idf = self.get_idf(term)
                tfidf = tf * idf
                magnitude_squared += tfidf**2

        magnitude = magnitude_squared**0.5  # sqrt

        self._magnitude_cache[doc_id] = magnitude  # put in the cache
        return magnitude

    def cosine_search(self, query_tokens: list[str], k: int = 10):
        query_vector = {}
        for term in query_tokens:
            if term in self.inverted_index:
                tf = query_tokens.count(term)
                idf = self.get_idf(term)
                query_vector[term] = tf * idf

        doc_scores: dict[str, float] = {}
        for term in query_vector:
            for doc_id in self.inverted_index[term]:
                # doc vector component
                doc_tf = self.get_tf(term, doc_id)
                doc_tfidf = doc_tf * self.get_idf(term)

                # dot product component
                doc_scores[doc_id] = (
                    doc_scores.get(doc_id, 0) + query_vector[term] * doc_tfidf
                )

        query_magnitude = sum(v**2 for v in query_vector.values()) ** 0.5

        # normalizing
        for doc_id in doc_scores:
            doc_magnitude = self._get_doc_magnitude(doc_id)
            doc_scores[doc_id] /= query_magnitude * doc_magnitude

        # best to worst
        ranked = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)

        if k > len(ranked):
            return ranked
        else:
            return ranked[:k]


# Attr:
# https://stackoverflow.com/questions/312443/how-do-i-split-a-list-into-equally-sized-chunks
def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def html_tokenizer(html_path: str):
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
        token_list = html_tokenizer(str(path))
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


def bigram(term: str):
    gram_set = set()
    togram = term + "$"
    curr = "$"

    for char in togram:
        curr += char

        if not (
            "$*" == curr or "*$" == curr
        ):  # Remove k-grams for when the `$` is right beside `*`, i.e., wilcard begins at the beginning or end
            gram_set.add(curr)

        curr = curr[1:]

    # Filter out wildcard bigrams
    gram_set = {item for item in gram_set if "*" not in item}

    return gram_set


def init_bigram_idx(terms: list[str]):
    kgram_idx: dict[str, list[str]] = {}

    for t in terms:
        bigrams = bigram(t)

        for b in bigrams:
            if b in kgram_idx:
                kgram_idx[b].append(t)
            else:
                kgram_idx.setdefault(b, [t])

    return kgram_idx


if "__main__" == __name__:
    index_obj = Index(Path("inverted_index.json"))

    exit(0)
