from pathlib import Path
from scrapy.linkextractors import LinkExtractor
from urllib.parse import urlparse
import scrapy
import uuid


class WebSpider(scrapy.Spider):
    name = "webcrawler"

    # default paths
    output_path = Path("output")
    default_url_file = "url.txt"

    # set default settings to spiders
    custom_settings = {
        # recommended setting for large and diverse corpus
        "DEPTH_LIMIT": 3,
        "CLOSESPIDER_PAGECOUNT": 5000,
        # autothrottle configs
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_START_DELAY": 1,
        "AUTOTHROTTLE_MAX_DELAY": 5,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.5,
        "CONCURRENT_REQUESTS": 16,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
        "ROBOTSTXT_OBEY": True,
        # dont flood my terminal ty
        # saving hash url mapping so windows dont fuck up the file saves
        "FEEDS": {
            "output/url_map.jsonl": {"format": "jsonlines"},
        },
    }

    @staticmethod
    def only_http_https(url: str):
        scheme = urlparse(url).scheme.lower()
        if scheme in {"", "http", "https"}:
            return url
        return None

    # scrapy's link extractor
    link_extractor = LinkExtractor(
        process_value=only_http_https,
        # non-exhaustive common patterns to avoid
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
        deny_extensions=["pdf", "zip", "gz", "tar", "7z", "rar"],  # Skip downloads
        tags=["a"],
        attrs=["href"],
        canonicalize=True,  # might be redundant with the http/https filtering after reading into it more, keeping it either way
        unique=True,
    )

    def __init__(self, url_file=default_url_file, *args, **kwargs):
        super(WebSpider, self).__init__(*args, **kwargs)

        url_fp = Path(url_file)

        if not url_fp.exists():
            raise FileNotFoundError(f"URL file doesnt exist\n     {url_fp.absolute()}")

        print(f"INFO: Crawling URLs listed @ {url_fp.absolute()}")

        with open(url_fp) as file:
            self.url_list = [line.rstrip() for line in file]

    async def start(self):
        for url in self.url_list:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.log(f"Scraped URL @ {response.url}")
        docID = str(uuid.uuid5(uuid.NAMESPACE_URL, response.url))

        # save for mapping
        yield {"docID": docID, "url": response.url}

        html_output_path = WebSpider.output_path / "html"
        filename = f"{docID}.html"

        Path(html_output_path).mkdir(parents=True, exist_ok=True)
        Path(html_output_path / filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")

        # recurse into next pages
        links = self.link_extractor.extract_links(response)
        yield from response.follow_all(links, callback=self.parse)
