import json
from pathlib import Path
import csv
import re
from nltk import edit_distance
from src.indexer.indexme import STOPWORDS, Index, bigram
from src.util.config import SRCH_LOGS, SRCH_LOGS_FP


def tokenizer(query: str):
    query_lowercase = query.lower()
    regex_p = r"[^\w\s]"
    tokens = re.sub(regex_p, "", query_lowercase).split()
    filtered_tokens = [t for t in tokens if t not in STOPWORDS]

    return filtered_tokens


def query_correction(query: list[str], bigram_idx: dict[str, list[str]]):
    corrected_query: list[str] = []
    correction_flag = False  # if correction occured, flip the flag

    for query_term in query:
        bigrams = bigram(query_term)

        # all candidate terms that match the bigrams
        candidate_terms: set[str] = set()
        for bg in bigrams:
            if bg in bigram_idx:
                candidate_terms.update(bigram_idx[bg])

        # no candidates found, keep original term
        if not candidate_terms:
            corrected_query.append(query_term)
            continue

        # best match
        min_distance = float("inf")
        best_match = query_term

        for candidate in candidate_terms:
            lev_dist = edit_distance(candidate, query_term)

            # exact match
            if lev_dist == 0:
                best_match = candidate
                break

            # update best match
            if lev_dist < min_distance:
                min_distance = lev_dist
                best_match = candidate

        if best_match != query_term:
            correction_flag = True

        corrected_query.append(best_match)

    return corrected_query, correction_flag


def get_url_mapping(url_map_fp: Path) -> dict[str, str]:
    if not url_map_fp.exists():
        raise FileNotFoundError(f"Expected file @ {url_map_fp}, but found nothing")

    with open(url_map_fp, "r") as f:
        return {json.loads(line)["docID"]: json.loads(line)["url"] for line in f}


def query_pipeline(query: str, index: Index, url_map: dict[str, str]):
    Path(SRCH_LOGS).mkdir(parents=True, exist_ok=True)

    q_tokenized = tokenizer(query)

    if not q_tokenized:
        raise ValueError("Processed query is empty!")

    q_corrected, flag = query_correction(q_tokenized, index.bigram_index)
    q_corrected_str = " ".join(q_corrected)

    documents = index.cosine_search(q_corrected)

    # handle non-existent and empty conditions (if it ever happens)
    file_exist = SRCH_LOGS_FP.exists() and SRCH_LOGS_FP.stat().st_size > 0

    with open(SRCH_LOGS_FP, "a", newline="") as query_log:
        writer = csv.DictWriter(
            query_log,
            fieldnames=[
                "query",
                "corrected_q",
                "is_corrected",
                "docid",
                "url",
                "score",
            ],
            delimiter=";",
        )

        if not file_exist:
            writer.writeheader()

        for doc_id, score in documents:
            writer.writerow(
                {
                    "query": query,
                    "corrected_q": q_corrected_str,
                    "is_corrected": flag,
                    "docid": doc_id,
                    "url": url_map[doc_id],
                    "score": score,
                }
            )

    return documents, q_corrected, flag


if "__main__" == __name__:
    whitespace = tokenizer("                 ")

    if not whitespace:
        raise ValueError("Processed query is empty!")

    exit(0)
