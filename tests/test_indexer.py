import unittest
import random
from pathlib import Path
from src.indexer.indexme import Index


class TestIndexer(unittest.TestCase):
    def test_index_identity(self):
        test_dir = Path(__file__).parent
        corpus_dir = test_dir / "fixtures" / "web-crawler" / "output"
        new_index_fp = test_dir / "fixtures" / "indexer" / "inverted_index.json"
        existing_index_fp = (
            test_dir / "fixtures" / "indexer" / "test_inverted_index.json"
        )

        # flush to test index creation
        if new_index_fp.exists():
            new_index_fp.unlink(missing_ok=True)
            print(f"Flushing directory @ {new_index_fp}")

        created_index = Index(new_index_fp, corpus_dir)
        self.assertTrue(
            new_index_fp.exists(), f"Created index must be written to {new_index_fp}"
        )

        existing_index = Index(existing_index_fp)

        self.assertEqual(
            set(created_index.inverted_index.keys()),
            set(existing_index.inverted_index.keys()),
            "Both indices should have same terms",
        )

        self.assertEqual(
            set(created_index.bigram_index.keys()),
            set(existing_index.bigram_index.keys()),
            "Both indices should have same bigrams",
        )

    def test_idf_consistency(self):
        random.seed(676767)

        test_dir = Path(__file__).parent
        new_index = test_dir / "fixtures" / "indexer" / "inverted_index.json"
        existing_index_fp = (
            test_dir / "fixtures" / "indexer" / "test_inverted_index.json"
        )

        new_index = Index(new_index)
        loaded_index = Index(existing_index_fp)

        terms = list(loaded_index.inverted_index.keys())
        for _ in range(1000):
            random_term = random.choice(terms)
            self.assertEqual(
                new_index.get_idf(random_term), loaded_index.get_idf(random_term)
            )


if "__main__" == __name__:
    unittest.main()
