"""The Moldy Fig Spider Entrypoint."""

import datetime
from typing import Generator

import dateparser

from scrape_from_the_ape.items import ScrapeFromTheApeItem

import scrapy


class MoldyFigSpider(scrapy.Spider):
    """The Moldy Fig Spider.

    Args:
        scrapy (scrapy.Spider): Scrapy Spider

    Yields:
        ScrapeFromTheApeItem: Conformed gig
    """

    name = "moldy_fig"
    start_urls = ["https://themoldyfig.com.au/whats-on/"]

    def parse(
        self: object, response: scrapy.http.TextResponse
    ) -> Generator[ScrapeFromTheApeItem, None, None]:
        """Method to parse each Moldy Fig listing & extract gig details.

        Args:
            response (scrapy.http.TextResponse): Moldy Fig What's on page

        Yields:
            Generator[ScrapeFromTheApeItem]: Each scraped gig
        """
        for gig in response.selector.css("article"):

            item = ScrapeFromTheApeItem()
            item["venue"] = self.name
            item["image_url"] = gig.css("img::attr(src)").extract_first()
            item["title"] = (
                gig.css("h3.mec-event-title")
                .css("a.mec-color-hover::text")
                .extract_first()
            )
            item["url"] = (
                gig.css("h3.mec-event-title")
                .css("a.mec-color-hover::attr(href)")
                .extract_first()
            )
            item["description"] = gig.css(
                "div.mec-event-description::text"
            ).extract_first()
            item["performance_date"] = dateparser.parse(
                gig.css("span.mec-start-date-label::text").extract_first()
            ).strftime("%Y-%m-%d")

            # Collect the generic time object so it can be used for start & doors
            start_time = dateparser.parse(
                gig.css("span.mec-start-time::text").extract_first()
            )
            item["music_starts"] = start_time.strftime("%H:%M")

            # Assume doors open 30min before music starts
            item["doors_open"] = (start_time - datetime.timedelta(minutes=30)).strftime(
                "%H:%M"
            )

            # The Moldy Fig is free but table bookings without food are $25pp
            item["price"] = 0

            yield item
