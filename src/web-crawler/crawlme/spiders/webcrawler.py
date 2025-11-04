from pathlib import Path
import scrapy


class WebSpider(scrapy.Spider):
    name = "webcrawler"

    # default paths
    output_path = Path("output")
    default_url_file = "url.txt"

    # set default settings to spiders
    custom_settings = {"DEPTH_LIMIT": 10, "CLOSESPIDER_PAGECOUNT": 5}

    def __init__(self, url_file=default_url_file, *args, **kwargs):
        super(WebSpider, self).__init__(*args, **kwargs)

        url_fp = Path(url_file)

        if not url_fp.exists():
            raise FileExistsError(f"URL file doesnt exist\n     {url_fp.absolute()}")

        print(f"INFO: Crawling URLs listed @ {url_fp.absolute()}")

        with open(url_fp) as file:
            self.url_list = [line.rstrip() for line in file]

    async def start(self):
        for url in self.url_list:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        self.log(f"Scraped URL @ {response.url}")
        page = response.url.split("//")[1].replace("/", "-")[:-1]   # make filename look nice and actually informative
        html_output_path = self.output_path / "html"
        filename = f"{self.name}_{page}.html"

        # make HTML output directory if it dont exist
        Path(html_output_path).mkdir(parents=True, exist_ok=True)

        Path(html_output_path / filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")

        # recurse into next pages
        next_page = response.css("a")
        yield from response.follow_all(next_page, callback=self.parse)

        # if next_page is not None:
        #     next_page = response.urljoin(next_page)

        #     yield scrapy.Request(next_page, callback=self.parse)
