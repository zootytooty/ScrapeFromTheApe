"""Birds Basement Spider Entrypoint."""

from typing import Generator

from scrape_from_the_ape.items import ScrapeFromTheApeItem
from scrape_from_the_ape.utils.birds_basement_helpers import birds_parser

import scrapy


class BirdsBasementSpider(scrapy.Spider):
    """Birds Basement Spider.

    Args:
        scrapy (scrapy.Spider): Scrapy Spider

    Yields:
        ScrapeFromTheApeItem: Conformed gig
    """

    name = "birds_basement"
    start_urls = ["https://birdsbasement.com/whats-on"]

    def parse(
        self: object, response: scrapy.http.TextResponse
    ) -> Generator[ScrapeFromTheApeItem, None, None]:
        """Method to parse each Birds Basement site & extract gig details.

        Args:
            response (scrapy.http.TextResponse): Birds Basement Homepage

        Yields:
            Generator[ScrapeFromTheApeItem]: Each scraped gig
        """
        # Parse the whole site in one big bang
        gigs = birds_parser(response)

        # Return each gig object back for scrapy to capture
        for gig in gigs:
            gig["venue"] = self.name
            yield gig
