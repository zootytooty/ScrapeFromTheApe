"""Uptown Jazz Cafe Spider Entrypoint."""

from typing import Generator

from scrape_from_the_ape.items import ScrapeFromTheApeItem
from scrape_from_the_ape.utils.uptown_helpers import uptown_parser

import scrapy


class UptownCafe(scrapy.Spider):

    name = "uptown_cafe"
    start_urls = ["https://www.uptownjazzcafe.com"]

    def parse(
        self: object, response: scrapy.http.TextResponse
    ) -> Generator[ScrapeFromTheApeItem, None, None]:
        """Method to parse Uptown & extract gig details.

        Args:
            response (scrapy.http.TextResponse): Uptown Homepage

        Yields:
            Generator[ScrapeFromTheApeItem]: Each scraped gig
        """
        # Parse the whole site in one big bang
        gigs = uptown_parser(response)

        # Return each gig object back for scrapy to capture
        for gig in gigs:
            gig["venue"] = self.name
            yield gig
