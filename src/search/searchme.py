from nltk import edit_distance


# Attr:
# Wikrama Wishnu Wardhana, wwardhana@hawki.illinoistech.edu
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


# Attr:
# Wikrama Wishnu Wardhana, wwardhana@hawki.illinoistech.edu
def init_kgram_idx(terms: list[str]):
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
    exit(0)
