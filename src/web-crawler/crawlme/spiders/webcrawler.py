from pathlib import Path
from typing import Any
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlparse
import scrapy
import uuid


class WebSpider(scrapy.Spider):
    name = "webcrawler"

    # default paths
    default_output_path = "output"
    default_url_file = "url.txt"
    allowed_domains = ["en.wikipedia.org"]

    custom_settings: dict[str, Any] = {
        "DEPTH_LIMIT": 3,
        "CLOSESPIDER_PAGECOUNT": 5000,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_MAX_DELAY": 5,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.5,
        "CONCURRENT_REQUESTS": 16,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
        "ROBOTSTXT_OBEY": True,
    }

    @staticmethod
    def only_http_https(url: str):
        scheme = urlparse(url).scheme.lower()
        if scheme in {"", "http", "https"}:
            return url
        return None

    link_extractor = LinkExtractor(
        process_value=only_http_https,
        allow_domains=["en.wikipedia.org"],
        deny=[
            r"/user/",
            r"/profile/",
            r"/account/",
            r"/login",
            r"/register",
            r"/signup",
            r"\?action=",
            r"/edit",
            r"/delete",
            r"/admin",
            r"/tag/",
            r"/category/",
            r"/archive/",
            r"/search",
            r"/share",
            r"/print",
            r"/comment",
            r"#comment",
        ],
        deny_extensions=["pdf", "zip", "gz", "tar", "7z", "rar"],
        tags=["a"],
        attrs=["href"],
        canonicalize=True,
        unique=True,
    )

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        output_path_arg = kwargs.get("output_path", cls.default_output_path)
        output_path = Path(output_path_arg)

        feeds = {
            str(output_path / "url_map.jsonl"): {"format": "jsonlines"},
        }
        crawler.settings.set("FEEDS", feeds, priority="spider")

        spider = super().from_crawler(crawler, *args, **kwargs)
        return spider

    def __init__(
        self,
        url_file: str = default_url_file,
        output_path: str = default_output_path,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.output_path = Path(output_path)

        url_fp = Path(url_file)
        if not url_fp.exists():
            raise FileNotFoundError(f"URL file doesnt exist\n     {url_fp.absolute()}")

        self.logger.info(f"Crawling URLs listed @ {url_fp.absolute()}")

        with open(url_fp) as file:
            self.url_list = [line.rstrip() for line in file if line.strip()]

    def start_requests(self):
        for url in self.url_list:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.log(f"Scraped URL @ {response.url}")
        docID = str(uuid.uuid5(uuid.NAMESPACE_URL, response.url))

        # save for mapping (goes into url_map.jsonl)
        yield {"docID": docID, "url": response.url}

        html_output_path = self.output_path / "html"
        filename = f"{docID}.html"

        html_output_path.mkdir(parents=True, exist_ok=True)
        (html_output_path / filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")

        links = self.link_extractor.extract_links(response)
        yield from response.follow_all(links, callback=self.parse)
