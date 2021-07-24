"""
Title: Brunswick Green Helpers
Desc: A collection of utility functions to organise parsing of Open Studio
"""

import requests
from datetime import datetime
from scrape_from_the_ape.items import *

BASE_URL = "https://thebrunswickgreen.com"


def brunswick_green_event_parser(gig: dict) -> ScrapeFromTheApeItem:
    """Main process to enrich & return gig data

    Args:
        gig (dict): JSON from Brunswick Green's API

    Returns:
        ScrapeFromTheApeItem: Scrape Item populated with Brunswick Green gig data
    """

    # startDate includes milliseconds
    start_datetime = datetime.utcfromtimestamp(int(gig["startDate"] / 1000.0))
    gig_url = f"{BASE_URL}{gig['fullUrl']}"

    item = ScrapeFromTheApeItem()

    item["title"] = gig["title"]
    item["music_starts"] = start_datetime.strftime("%Y-%m-%d %H:%M:%S")
    item["doors_open"] = start_datetime.strftime("%Y-%m-%d")
    item["performance_date"] = start_datetime.strftime("%Y-%m-%d")
    item["price"] = 0.00  # no prices in API, gig page, or when following ticket links 😟
    item["description"] = get_description(gig_url)
    item["url"] = gig_url
    item["image_url"] = gig["assetUrl"]

    return item


def get_description(gig_url: str) -> str:
    """Find and make nice the gig description from a single event from Brunswick Green website

    Args:
        gig_url (str): The url for the gig

    Returns:
        str: Event Description, maybe an empty string

    """

    gigpage = scrapy.http.HtmlResponse(
        url="Gig",
        body=(
            requests.get(
                "http://www.thebrunswickgreen.com/gigs-at-the-green/2021/3/21/the-steamboat-whistlers"
            )
        ).text,
        encoding="utf-8",
    )

    event = (
        gigpage.css(".eventitem-column-content").css(".sqs-block-content").xpath("//p")
    )

    # strip the last two paragraphs - an empty string and a square space plug
    description = "\n".join(
        "".join(line.strip() for line in p.xpath(".//text()").extract() if line.strip())
        for p in event[:-2]
    )

    return description
