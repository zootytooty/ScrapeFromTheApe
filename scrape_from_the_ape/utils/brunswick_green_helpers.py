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

    return "giggity"
