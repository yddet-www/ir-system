from pathlib import Path
import unittest
from src.indexer.indexme import Index
from src.search.searchme import (
    tokenizer,
    query_correction,
    query_pipeline,
    get_url_mapping,
)


class TestSearch(unittest.TestCase):
    def setUp(self):
        test_dir = Path(__file__).parent
        index_fp = test_dir / "fixtures" / "indexer" / "test_inverted_index.json"
        output_dir = test_dir / "fixtures" / "web-crawler" / "output"
        url_map_fp = output_dir / "url_map.jsonl"

        self.index_obj = Index(index_fp)
        self.url_maps = get_url_mapping(url_map_fp)

    def test_tokenizer(self):
        query = "cafe near me serving matcha"
        output = tokenizer(query)
        expected = ["cafe", "near", "serving", "matcha"]
        self.assertEqual(output, expected)

        query = "the thinker is not much better than the thinkee"
        expected = ["thinker", "much", "better", "thinkee"]
        output = tokenizer(query)
        self.assertEqual(output, expected)

        query = "wHy ArE YoU AlWaYs LIke THIS"
        expected = ["always", "like"]
        output = tokenizer(query)
        self.assertEqual(output, expected)

        query = "                who left this      whitespace        "
        expected = ["left", "whitespace"]
        output = tokenizer(query)
        self.assertEqual(output, expected)

        query = "I'm so, so ANGRY WITH YOU! D'you know that!?"
        expected = ["im", "angry", "dyou", "know"]
        output = tokenizer(query)
        self.assertEqual(output, expected)

        query = "to be or not to be"
        expected = []
        output = tokenizer(query)
        self.assertEqual(output, expected)

        query = "               "
        expected = []
        output = tokenizer(query)
        self.assertEqual(output, expected)

    def test_query_correction(self):
        query = tokenizer("mattison Turing")
        correction, flag = query_correction(query, self.index_obj.bigram_index)
        expected = ["mathison", "turing"]
        self.assertEqual(correction, expected)
        self.assertTrue(flag)

        query = tokenizer("douglas hofstater")
        correction, flag = query_correction(query, self.index_obj.bigram_index)
        expected = ["douglas", "hofstadter"]
        self.assertEqual(correction, expected)
        self.assertTrue(flag)

        query = tokenizer("Alan Turing")
        correction, flag = query_correction(query, self.index_obj.bigram_index)
        expected = ["alan", "turing"]
        self.assertEqual(correction, expected)
        self.assertFalse(flag)

    def test_query_pipeline(self):
        query = "Alan Turing world war contribution"
        output, _, _ = query_pipeline(query, self.index_obj, self.url_maps)
        check_order = sorted(output, key=lambda x: x[1], reverse=True)
        self.assertEqual(len(output), 10)
        self.assertEqual(output, check_order)

        with self.assertRaises(ValueError):
            query = " "
            output, _, _ = query_pipeline(query, self.index_obj, self.url_maps)

        with self.assertRaises(ValueError):
            query = "to be or not to be"
            output, _, _ = query_pipeline(query, self.index_obj, self.url_maps)


if "__main__" == __name__:
    unittest.main()
