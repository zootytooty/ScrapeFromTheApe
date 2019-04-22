"""
Title: Birds Basement Helpers
Desc:  A collection of utility functions to organise parsing birds basement
"""

import json
from datetime import timedelta, datetime
import requests
from scrape_from_the_ape.items import *
import scrapy

# Utility Fns
import scrape_from_the_ape.utils.datetime_helpers as dth
import scrape_from_the_ape.utils.utils as ut


def content_extractor(html):
    """Extract show objects from raw HTML
    
    Args:
        html (scrapy.http.response.html.HtmlResponse): Scrapy html response for Birds Basement

    Returns:
        list: Array on show objects
    """

    # Shows are JSON objects within JS scripts
    scripts = html.css("script::text").extract()

    # "showz" is the variable now with show objects
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
    delta = max(dates) - min(dates)

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
    

    # Determine doors open & start time
    start_time = get_start_time(gig['urlInfo'])
    start_time = dth.get_timestamp(start_time)

    doors_open = calc_open_doors(start_time)
    doors_open = dth.get_timestamp(doors_open)

    # For consistency we want a new object for each date a show is to be played
    gigs = []
    for date in dates:

        item = ScrapeFromTheApeItem()

        item['title'] = gig['title']
        item['music_starts'] = start_time
        item['doors_open'] = doors_open
        item['performance_date'] = date
        item['price'] = ut.parse_price(gig['price'])
        item['description'] = gig['text']
        item['url'] = gig['urlInfo']
        item['image_url'] = gig['imgUrl']

        gigs.append(item)

    return gigs


def is_time(time_string: str):
    """ Checks whether a string is a time
    
    Args:
        time_string (str): String to check
    
    Returns:
        boolean: True/False indicator for whether or not the string is a time
    """

    # Remove any am/pm identifiers
    time_string = time_string.lower().replace('am','').replace('pm','').strip()

    # Timestamp conversion attempt will identity times vs other
    try:
        datetime.strptime(time_string, '%H:%M')
        return True
    except ValueError:
        return False


def get_start_time(show_url: str, show_identifier: str = "Show:"):
    """Extract show start time from gig site
    
    Args:
        show_url (str): Birds basebasement specific show page
        show_identifier (str, optional): Defaults to "Show:". Start time prefix to split on
    
    Returns:
        str: Start Time
    """

    # Downloads HTML & creates a scrapy object
    response = scrapy.http.HtmlResponse(url = "Birds Gig", body=(requests.get(show_url)).text, encoding='utf-8')

    # The "n-text" class corressponds to the price & start time items
    show_items = [x.strip() for x in response.css(".n-text p::text").extract() if x.strip() != '' and show_identifier in x]

    # If the above worked correctly there should only be 1 item returned
    # Need to figure out how to handles situations when that's not true.
    if len(show_items) == 1:
        start_splits = [x.strip() for x in show_items[0].split(show_identifier)]

        # One of the split items should be a string containing the start time
        # Check for & return that
        return [x for x in start_splits if is_time(x)][0]



def calc_open_doors(start_time: str):
    """Given start time, calculates the time doors open
    From: https://birdsbasement.com/help
    
    Args:
        start_time (str): Show start time
    
    Returns:
        str: Doors open time
    """

    # Convert to proper time object
    start_time = datetime.strptime(start_time, '%H:%M')
    
    # Early gigs
    if start_time.hour < 10:
        return "18:00"
    else:
        return "22:00"