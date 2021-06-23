"""Scrapy pipeline settings."""

import requests

from scrape_from_the_ape.items import ScrapeFromTheApeItem

from scrapy import spiders


class ScrapeFromTheApePipeline(object):
    """General pipeline for scraping & storing gigs."""

    def __init__(self: object) -> None:
        """Sets up object to store identified gigs."""
        self.all_gigs = []

    def close_spider(self: object, spider: spiders) -> None:
        """Save all results to the database.

        Runs after scraping the sight

        Args:
            spider (spider): Scrapy Spider
        """
        _ = requests.post(
            url="https://v3dl6mmgz1.execute-api.ap-southeast-2.amazonaws.com/dev/gigs",
            json=self.all_gigs,
        )

    def process_item(
        self, item: ScrapeFromTheApeItem, spider: spiders
    ) -> ScrapeFromTheApeItem:
        """Store each scraped gig for later upload to DB.

        Args:
            item (ScrapeFromTheApeItem]): Scraped gig to store
            spider (spider): Scrapy Spider

        Returns:
            ScrapeFromTheApeItem: Return the input item to carry on with
        """
        # Capture item to store once all scraping is complete
        # noting they must be dictionaries in order to send to the API
        self.all_gigs.append(dict(item))

        return item
