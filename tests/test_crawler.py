import unittest
import subprocess
import shutil
import sys
from pathlib import Path
from src.search.searchme import get_url_mapping


class TestWebCrawler(unittest.TestCase):
    def test_crawler(self):
        test_dir = Path(__file__).parent
        crawler_dir = test_dir.parent / "src" / "web-crawler"

        output_dir = test_dir / "fixtures" / "web-crawler" / "output"
        seed_url = test_dir / "fixtures" / "web-crawler" / "test_urls.txt"

        cmd = [
            sys.executable,
            "-m",
            "scrapy",
            "crawl",
            "webcrawler",
            "-s",
            "CLOSESPIDER_PAGECOUNT=50",  # for the sake of testing, limit to just 50
            "-a",
            f"url_file={str(seed_url)}",
            "-a",
            f"output_path={str(output_dir)}",
        ]

        if output_dir.exists():
            shutil.rmtree(output_dir)
            print(f"Flushing directory @ {output_dir}")

        result = subprocess.run(
            cmd, cwd=crawler_dir, check=True  # Run from web-crawler directory
        )

        url_map_fp = output_dir / "url_map.jsonl"
        html_dir = output_dir / "html"

        self.assertTrue(url_map_fp.exists() and html_dir.exists())

        # borrowing a function, technically testing it too
        url_maps = get_url_mapping(url_map_fp).keys()

        # check if each scraped html exists in the mapping file
        for html in html_dir.iterdir():
            doc_id = html.name[:-5]  # remove '.html'
            self.assertIn(doc_id, url_maps)


if "__main__" == __name__:
    unittest.main()
