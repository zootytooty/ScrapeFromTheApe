""""

"""

import json
from datetime import timedelta, datetime
from scrape_from_the_ape.items import *


def content_extractor(html):
    """Extract show objects from raw HTML
    
    Args:
        html (scrapy.http.response.html.HtmlResponse): Scrapy html response for Birds Basement

    Returns:
        list: Array on show objects
    """

    # Shows are JSON objects within JS scripts
    scripts = html.css("script::text").extract()

    # showz is the variable now with show objects
    shows = [script for script in scripts if "var showz = " in script]
    show_splits = shows[0].split("var showz = ")

    # Convert Shows to JSON
    # It contains a little trailing junk that we need to remove before it's a proper JSON
    return json.loads(show_splits[1].strip(";\n"))


def date_range_generator(dates: list):
    """Generates a range of dates between two
    
    Args:
        dates (list): List containing first & last date
    
    Returns:
        list: list of dates from first & last date
    """

    # Convert to datetime objects
    dates = [datetime.strptime(date, "%Y-%m-%d") for date in dates]

    # Determine how many days to count forward
    delta = dates[1] - dates[0]

    # Generate date range
    return [(dates[0] + timedelta(i)).strftime("%Y-%m-%d") for i in range(delta.days + 1)]


def birds_parser(gig: dict):
    """Main process to enrich & return gig data
    
    Args:
        gig (dict): Show Object from Birds Basement
    
    Returns:
        list: List of Scrape Items populated with Birds Basement gig data
    """

    # Builds an array of dates to iterate over
    # Some shows only happen on 1 night so we don't need to enrich that
    dates = list(set(gig['date']))
    if len(dates) == 2:
        dates = date_range_generator(dates)
    
    # For consistency we want a new object for each date a show is to be played
    gigs = []
    for date in dates:

        item = ScrapeFromTheApeItem()

        item['title'] = gig['title']
        # item['music_starts'] =
        # item['doors_open'] =
        item['date'] = date
        item['price'] = gig['price']
        item['desc'] = gig['text']
        item['url'] = gig['urlInfo']
        item['image_url'] = gig['imgUrl']

        gigs.append(item)

    return gigs