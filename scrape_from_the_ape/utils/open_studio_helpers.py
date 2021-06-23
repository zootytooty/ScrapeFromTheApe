"""
Title: Open Studio Helpers
Desc: A collection of utility functions to organise parsing of Open Studio
"""

from datetime import datetime
import requests
from scrape_from_the_ape.items import *
import scrapy
import dateparser
import re

def open_studio_event_parser(in_event):
    """Main process to enrich & return gig data
    
    Args:
        in_event (str): Open Studio individual show url
    
    Returns:
        ScrapeFromTheApeItem: Scrape Item populated with Open Studio gig data
    """

    gig = ScrapeFromTheApeItem()
    date = get_event_date(in_event)  
    start_time = get_start_time(in_event)

    gig['date'] = date
    gig['doors_open'] = calc_open_doors(date)
    gig['music_starts'] = start_time
    
    #Clean up the markup, there are lots of empty divs shoving a \n into our description
    descr = parse_event_description(in_event)
    #Clean up the price
    price = parse_event_cost(in_event)

    # Show details
    gig['title'] = in_event.css(".tribe-events-single-event-title::text").extract_first()
    gig['price'] = price
    gig['description'] = descr
    gig['url'] = in_event.request.url
    gig['image_url'] = in_event.css("div#tribe-events-single-event-meta-wrapper img::attr(src)").extract_first()

    
    return gig

def parse_event_cost(in_event):
    """Find and make nice the gig cost from a single event from open studio website
    
    Args:
        in_event (scrapy.http.response.html.HtmlResponse): The html response for the single event from open studio website
    
    Returns:
        str: Event Cost, empty string if cannot find something
    
    """

    temp_price = in_event.css(".tribe-events-event-cost2::text").extract_first()
    if temp_price is None:
        return ""
    
    return re.sub('\s+','',temp_price)

def parse_event_description(in_event):
    """Find and make nice the gig description from a single event from open studio website
    
    Args:
        in_event (scrapy.http.response.html.HtmlResponse): The html response for the single event from open studio website
    
    Returns:
        str: Event Description, maybe an empty string
    
    """

    #Clean up the markup, there are lots of empty divs shoving a \n into our description
    descrip_html = in_event.css(".tribe-events-single-event-description ::text").extract()
    descr = ""
    for str_x in descrip_html:
        temp_clean_str = str_x.strip('\n').strip('\t')
        if len(temp_clean_str) != 0:
            descr = "".join([descr,str_x,'\n'])
    return descr


def calc_open_doors(event_date: str):
    """Given event date, calculates the time doors open
    From: https://www.facebook.com/pg/openstudio.bar/about/?ref=page_internal - Open times for venue, not really a doors open policy, just open times
    
    Args:
        event_date (str): Show date in format %Y-%m-%d
    
    Returns:
        str: Doors open time or None if date is invalid
    """
    
    # Create a date object
    try:
        temp_date = datetime.strptime(event_date, '%Y-%m-%d')
    except ValueError:
        return None

    # Open venue so doors open 19:00 on weekday and 13:30 on weekends according to bar facebook page
    if temp_date.weekday() >=5:
        return "7:00 pm"
    else:
        return "1:30 pm"

def get_event_date(in_event):
    """Extract show start time from a string
    
    Args:
        in_event (scrapy.http.response.html.HtmlResponse): The html response for the single event from open studio website
    
    Returns:
        str: Event Date ("%Y-%m-%d") or None if unsuccessful
    """
    
    # Datetime Info
    # expected format from Open studio is in the correct style, but the parser will help verify it
    event_date = in_event.css(".tribe-events-start-date::attr(title)").extract_first()
    event_date1 = in_event.css(".tribe-events-start-datetime::attr(title)").extract_first()
    event_date2 = in_event.css(".tribe-events-start-date::text").extract_first()
    event_date3 = in_event.css(".tribe-events-start-datetime::text").extract_first()
    if event_date is not None:
        temp_date = dateparser.parse(event_date)
    elif event_date2 is not None:
        #Try to use the contents of the element rather than the attribute title (unfortunately this is problematic as the year isn't clear, but we can guess that)
        #Need to catch the error here as well if the selector is empty/non-existant
        temp_date = dateparser.parse(event_date2, settings={'PREFER_DATES_FROM': 'future'})
    elif event_date1 is not None:
        temp_date = dateparser.parse(event_date1)
    elif event_date3 is not None:
        temp_date = dateparser.parse(event_date3, settings={'PREFER_DATES_FROM': 'future'})
    else:
        #Need to determine best fallback
        return None
    
    return temp_date.strftime("%Y-%m-%d")

def get_start_time(in_event):
    """Extract show start time from a string
    
    Args:
        in_event (scrapy.http.response.html.HtmlResponse): The html response for the single event from open studio website
    
    Returns:
        str: Start Time or None if unsuccessful
    """
    
    temp_time = in_event.css(".tribe-events-start-time::text").extract_first()
    if temp_time is not None:
        temp_time = temp_time.strip()
        #Open Studio format is 'Time: 0:00 pm - 0:00 pm'
        #Strip the front 'Time:' prefix if its there and get the first occurance of what might look like a time and its suffix (am/pm)
        first_time = re.search(r"\d+[:]*\d*[ ]*\D{2}",temp_time)
        if first_time:
            temp_time = dateparser.parse(first_time[0])
            try:
                temp_time = temp_time.strftime("%-I:%M %p")
            except ValueError:
                return None
        else:
            temp_time = None
    
    return temp_time