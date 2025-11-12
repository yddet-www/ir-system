from src.util.config import CRWL_MAPPING, CRWL_OUTPUT, CRWL_HTML
from bs4 import BeautifulSoup
from pathlib import Path


def parse_doc(html_path: str):
    p = Path(html_path)

    # Attr:
    # http://xahlee.info/python/charset_encoding.html
    # Change file encoding to utf-8
    with open(p, encoding="utf-8") as html:
        soup_obj = BeautifulSoup(html, "html.parser")
        content = soup_obj.get_text(" ", strip=True)

    # print(content)

    return content


if "__main__" == __name__:
    path = CRWL_HTML / "9b111d43-6cc5-55ad-a74a-bf9e1a921fd2.html"
    text_content = parse_doc(str(path))
    # print(text_content)

    exit(0)
