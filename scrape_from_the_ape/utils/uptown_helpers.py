"""Utilities to scrape Uptown Jazz Cafe gigs."""

import re
from typing import List, Tuple

import dateparser

from scrape_from_the_ape.items import ScrapeFromTheApeItem

import scrapy
from scrapy.http import TextResponse


def uptown_parser(site: TextResponse) -> List[ScrapeFromTheApeItem]:
    """Top level parser for extracting details from Uptown.

    Listings on homepage: https://www.uptownjazzcafe.com/

    Args:
        site (scrapy.http.response.text.TextResponse): Scraped homepage content

    Returns:
        List[ScrapeFromTheApeItem]: All the scraped gig details
    """
    gigs = []
    for gig in site.xpath("//*[contains(@id, 'gig')]"):

        is_gig = gig.css("strong").extract_first()
        if is_gig:

            item = ScrapeFromTheApeItem()

            # All retrieved from the Birds homepage
            item["performance_date"], item["title"] = extract_date_title(is_gig)

            # There are no individual show pages
            item["url"] = "https://www.uptownjazzcafe.com"
            item[
                "image_url"
            ] = f"{item['url']}/{gig.css('img::attr(src)').extract_first()}"

            # Description contains price & time info.
            # Get that first then build the rest
            item["description"] = extract_description(gig)
            item["price"] = extract_price(item["description"])

            doors_open, start_time = extract_timings(item["description"])
            item["doors_open"] = doors_open
            item["music_starts"] = start_time

            gigs.append(item)

    return gigs


def extract_description(gig_selector: scrapy.selector.unified.Selector) -> str:
    """Crunches text blob into single string.

    Args:
        gig_selector (scrapy.selector.unified.Selector): Selector containing gig-info-wrap

    Returns:
        str: All text items concatenated & semi-cleaned
    """
    description = gig_selector.css("div.gig-info-wrap *::text").extract()
    description = " ".join(description)
    description = (
        description.replace("\n", "")
        .replace("\r", "")
        .replace("\xa0", "")
        .replace("\t", "")
        .strip()
    )
    return description


def extract_price(string: str) -> float:
    """Extracts price from body of text.

    Notes:
        - With some work this could likely be turned into a generic function for all spiders to use.
        - Only works with "$"
        - If multiple prices are present only the first is extracted,
            eg concession $10, full $20 would just return 10.0

    Args:
        string (str): Text blob containing price

    Returns:
        float: Extracted price
    """
    price_match = re.search(r"(?:\$)\s*([\d,]+(?:\.\d{2})?)", string)
    price = 0
    if price_match:
        price = float(price_match.group().replace("$", ""))

    return price


def extract_timings(string: str) -> Tuple[str, str]:
    """Searches a body of text & returns doors open & start time.

    It's an absolute monstrosity & likely not maintainable.
    With some work this could likely be turned into a generic function for all spiders to use.
    Note:
        - If multiple shows are listed it returns the first.
            Eg shows at 8pm and 10pm will only return 8pm

    Args:
        string (str): Text blob containing times

    Returns:
        Tuple[str, str]: doors open time & music start time
    """
    doors_open = None
    start_time = None
    doors_open_pattern = re.compile(
        r"(?<=Doors|doors) (?:1[0-2]|0?[1-9])(?::|.(?:[0-5][0-9]))?(?:AM|PM|am|pm)"
    )
    music_at_patterns = [
        re.compile(
            r"(?<=music at) (?:1[0-2]|0?[1-9])(?::|.(?:[0-5][0-9]))?(?:AM|PM|am|pm)"
        ),
        re.compile(
            r"(?<=music starts at) (?:1[0-2]|0?[1-9])(?::|.(?:[0-5][0-9]))?(?:AM|PM|am|pm)"
        ),
    ]
    doors_open_matches = re.search(doors_open_pattern, string)
    if doors_open_matches:
        doors_open = doors_open_matches.group().strip()
        doors_open = None if doors_open == "" else doors_open

    music_at_matches = [
        re.search(pattern, string)
        for pattern in music_at_patterns
        if re.search(pattern, string) is not None
    ]
    if len(music_at_matches) > 0:
        start_time = music_at_matches[0].group().strip()
        start_time = None if start_time == "" else start_time

    if start_time is None:
        generic_start_pattern = re.compile(
            r"(?:1[0-2]|0?[1-9])(?::|.(?:[0-5][0-9]))?(?:AM|PM|am|pm)"
        )
        starts_at_matches = re.search(generic_start_pattern, string)
        if starts_at_matches:
            start_time = starts_at_matches.group().strip()
        else:
            start_time = "8:30pm"

    if doors_open is None:
        if start_time == "8pm" or start_time == "8:00pm":
            doors_open = "7:30pm"
        else:
            doors_open = "8:00pm"

    return dateparser.parse(doors_open).strftime("%H:%M"), dateparser.parse(
        start_time
    ).strftime("%H:%M")


def extract_date_title(
    gig_present: str,
) -> Tuple[str, str]:
    """Attempts to extract performance date & show title.

    Notes:
        - Current implementation assumes all text after the date it the title.
            This is a false assumption

    Args:
        gig_present (str): Band text blob

    Returns:
        Tuple[str, str]: Performance date & Show Title
    """
    # Extract the text chunks that contain the date & title info
    band_info_selector = scrapy.Selector(text=gig_present).xpath(".//text()").extract()
    info_parts = [x.replace("\r\n", "") for x in band_info_selector if x != "\r\n"]

    gig_date, date_index = extract_date(info_parts)

    # Infer the gig name as all the parts following the date.
    # This doesn't always work but is generally close/good enough
    gig_name = " ".join(info_parts[date_index + 1: len(info_parts)]).lower().title()

    return gig_date, gig_name


def extract_date(band_info_parts: list) -> Tuple[str, int]:
    """Extracts date from list.

    Examines a list and turns the first date-like element into a datetime.
    Using just month strings for the search is crude & this could likely be turned into a
     more general function

    Args:
        band_info_parts (list): Collection of elements of which some may contain a datetime string

    Returns:
        Tuple[str, int]: First performance date, list index of performance date
    """
    # Try & identify the element representing the date
    # This is rudimentary but hopefully sufficient for the interim
    months = [
        "january",
        "february",
        "march",
        "april",
        "may",
        "june",
        "july",
        "august",
        "september",
        "october",
        "november",
        "december",
    ]
    is_date = [x.lower().startswith(tuple(months)) for x in band_info_parts]
    index_of_date = [i for i, x in enumerate(is_date) if x][0]

    # Converts it into a timestamp object
    gig_date = dateparser.parse(band_info_parts[index_of_date]).strftime("%Y-%m-%d")

    return gig_date, index_of_date
