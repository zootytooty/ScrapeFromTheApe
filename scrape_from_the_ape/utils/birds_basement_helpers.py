"""Utilities to scrape Birds Basement gigs."""

import re
from datetime import datetime, timedelta
from typing import List, Tuple

import requests

from scrape_from_the_ape.items import ScrapeFromTheApeItem

from scrapy.http import TextResponse
from scrapy.selector import unified


def birds_parser(site: TextResponse,) -> List[ScrapeFromTheApeItem]:
    """Top level parser for extracting details from birds basement.

    Listings on homepage: https://birdsbasement.com/

    Args:
        site (scrapy.http.response.text.TextResponse): Scraped homepage content

    Returns:
        List[ScrapeFromTheApeItem]: All the scraped gig details
    """
    gigs = []
    for gig in site.css(".col-md-6"):

        item = ScrapeFromTheApeItem()

        # All retrieved from the Birds homepage
        item["title"] = extract_element(gig, "h2.tile-title")
        item["description"] = extract_element(gig, "div.tile-desc")
        item["performance_date"] = extract_show_date(gig)
        item["url"] = extract_element(gig, "a::attr(href)")
        item["image_url"] = extract_image(gig)

        # Retrieved from the individual show info
        price, start_time = extract_others(item["url"])
        item["price"] = price
        item["music_starts"] = start_time
        item["doors_open"] = calc_open_doors(start_time)

        gigs.append(item)

    return gigs


def extract_others(url: str) -> Tuple[float, str]:
    """Scrapes dedicated gig page to extract price & start time.

    Args:
        url (str): Direct URL to the site

    Returns:
        Tuple[float, str]: price & start time of the gig
    """
    # Get the new page
    r = requests.get(url)
    response = TextResponse(r.url, body=r.text, encoding="utf-8")

    # Contains price & timing details
    info_paragraph = response.css("div.col-md-3").css("div._brake-text").css("p")

    price = extract_price(info_paragraph)
    start_time = extract_start_time(info_paragraph)

    return price, start_time


def extract_price(paragraph: TextResponse) -> float:
    """Parses the main paragraph containing the shows details for price.

    Args:
        paragraph (TextResponse): HTML paragraph object of the show details

    Returns:
        float: Show price
    """
    # Get 'Book Tickets' text block
    book_tickets = paragraph.extract_first()

    # Extract price by grabbing numbers following '$', eg 44.4 from $44.4
    prices = re.findall(r"(?:[^\$]{1}[,\d]+\.?\d*)", book_tickets)
    if len(prices) > 0:
        return float(prices[0])
    else:
        return None


def extract_start_time(paragraph: TextResponse) -> str:
    """Parse the main paragraph containing the shows details for start time.

    Args:
        paragraph (TextResponse): HTML paragraph object of the show details

    Returns:
        str: Earliest start time
    """
    all_paragraphs = paragraph.extract()
    time_present = [
        x for x in all_paragraphs if "Show" in x and ("am" in x or "pm" in x)
    ][0]

    start_time = re.findall(r"Show:\s(\d{1,2}\:\d{2}\s?(?:AM|PM|am|pm))", time_present)

    if len(start_time) > 0:
        start_time = datetime.strptime(start_time[0], "%I:%M %p").strftime("%H:%M")
        return start_time
    else:
        return None


def extract_image(item: unified.Selector) -> str:
    """Extracts the image URL.

    Args:
        item (unified.Selector): Text block containing the image url

    Returns:
        str: URL of the cover image
    """
    # Extract image path info
    html_image_url = item.xpath("descendant-or-self::img").extract_first()

    # Strip out html junk
    image_url = re.findall(r"src=\'(.+?)\'", html_image_url)

    if len(image_url) > 0:
        # URL contains width & height info we don't require
        return image_url[0].split("--")[0]
    else:
        return None


def extract_show_date(item: unified.Selector) -> str:
    """Extract show date from the object containing show summary info.

    Args:
        item (unified.Selector): Show summary object

    Returns:
        str: The range of dates for the show
    """
    # Extract performance date class
    # Select first because it returns a duplicate
    html_show_date = item.css("div.tile-date").extract_first()

    # Remove the html junk surrounding the true value
    show_date = re.sub(r"<[^>]+>", "", html_show_date).strip()

    # Extract date & convert format
    # This actually returns a range of dates for shows but for
    # now extract just the initial date
    show_date = show_date.split(",")[1].strip().split(" - ")[0]
    show_date = datetime.strptime(show_date, "%d %B %Y").strftime("%Y-%m-%d")
    return show_date


def extract_element(item: unified.Selector, css: str) -> str:
    """General element extract method based on the object containing show summary info.

    Args:
        item (unified.Selector): Show summary object
        css (str): Pattern to extract show info

    Returns:
        str: Extracted element
    """
    # Extract requested class
    # Select first because it returns a duplicate
    html_item = item.css(css).extract_first()

    # Remove the html junk surrounding the true value
    clean_item = re.sub(r"<[^>]+>", "", html_item).strip()
    return clean_item


def date_range_generator(dates: list) -> List[datetime]:
    """Generates a range of dates between two.

    Args:
        dates (list): List containing first & last date

    Returns:
        List[datetime]: list of dates from first & last date
    """
    # Convert to datetime objects
    dates = [datetime.strptime(date, "%Y-%m-%d") for date in dates]

    # Determine how many days to count forward
    delta = max(dates) - min(dates)

    # Generate date range
    return [
        (dates[0] + timedelta(i)).strftime("%Y-%m-%d") for i in range(delta.days + 1)
    ]


def calc_open_doors(start_time: str) -> str:
    """Given start time, derives the time doors open.

    From: https://birdsbasement.com/help

    Args:
        start_time (str): Show start time

    Returns:
        str: Doors open time
    """
    # Convert to proper time object
    start_time = datetime.strptime(start_time, "%H:%M")

    # Early gigs
    if start_time.hour < 21:
        return "18:00"
    else:
        return "21:15"
