"""
Title: Bar 303 Helpers
Desc: A collection of utility functions to organise parsing of Open Studio
"""

from datetime import datetime
import requests
from scrape_from_the_ape.items import *
import scrapy
import dateparser
import re

# Utility Fns
import scrape_from_the_ape.utils.datetime_helpers as dth
import scrape_from_the_ape.utils.utils as ut


def bar303_event_parser(in_event, base_url : str):
    """Main process to enrich & return gig data
    
    Args:
        in_event (scrapy.http.response.html.HtmlResponse): Bar 303 individual show html response portion
        base_url (str): The base url to construct any relative links in the content
        
    Returns:
        ScrapeFromTheApeItem: Scrape Item populated with Bar 303 gig data
    """

    gig = ScrapeFromTheApeItem()
    descrip_html = parse_event_description(in_event)

    price = parse_event_cost(descrip_html)
    price = ut.parse_price(price)

    doors_open = calc_open_doors(descrip_html)
    doors_open = dth.get_timestamp(doors_open)

    music_starts = get_start_time(in_event)
    music_starts = dth.get_timestamp(music_starts)

    gig['performance_date'] = get_event_date(in_event) 
    gig['doors_open'] = doors_open
    gig['music_starts'] = music_starts
    gig['description'] = descrip_html
    gig['price'] = price
    
    
    # Get the main image, or an alternate if it doesn't exist
    img = in_event.css(".eventlist-column-thumbnail img::attr(src)").extract_first()
    if not img:
        img = in_event.css(".eventlist-description img::attr(src)").extract_first()
    gig['image_url'] = img
    
    # Show details
    title = in_event.css(".eventlist-title a::text").extract_first()
    if title:
        gig['title'] = title
    else:
        gig['title'] = ""
    
    gig_url = ''.join([base_url,in_event.css(".eventlist-title a::attr(href)").extract_first()])
    if gig_url:
        gig['url'] = gig_url
    else:
        gig['url'] = ""
    
    return gig

def parse_event_cost(descr: str):
    """Find and make nice the gig cost from a single event from bar 303 website
    
    Args:
        descrip_html (str): The html description string for the single event from bar 303 website
    
    Returns:
        str: Event Cost, empty string if cannot find something
    
    """

    # First attempt, lets find a $ symbol and pull the sentance or line its on as the price
    price = re.findall("[^\n.|\-,]*[$][ ]*\d+[^\n.|\-,]*",descr)
    if not price:
        # Ok lets see if its a donation or free
        price = re.search("free|donation",descr,re.I)
        if price:
            price = price[0]
        else:
            # Ok we cannot determine the price
            price = ""
    else:
        price = ". ".join(x.strip() for x in price)
    
    return price

def parse_event_description(in_event):
    """Find and make nice the gig description from a single event from bar 303 website
    
    Args:
        in_event (scrapy.http.response.html.HtmlResponse): The html response for the single event from bar 303 website
    
    Returns:
        str: Event Description, maybe an empty string
    
    """
    
    #Clean up the markup, there are lots of empty divs shoving a \n into our description
    descrip_html = in_event.css(".eventlist-description .sqs-block-html ::text").extract()
    descr = ""
    for str_x in descrip_html:
        temp_clean_str = str_x.strip('\n').strip('\t')
        if len(temp_clean_str) != 0:
            descr = "".join([descr,str_x,'\n'])
    return descr


def calc_open_doors(descr: str):
    """Given event description, searches for the time doors open
    
    Args:
        descr (str): Show description to search
    
    Returns:
        str: Doors open time or "" if date is invalid
    """
    
    # Doors open calculate from the description
    doors_open = re.search("[^\n.|\-,]*doors[^\n.|\-,]*",descr,re.I)
    if doors_open:
        return doors_open[0].strip()
    else:
        return ""

def get_event_date(in_event):
    """Extract show start time from a string
    
    Args:
        in_event (scrapy.http.response.html.HtmlResponse): The html response for the single event from bar 303 website
    
    Returns:
        str: Event Date ("%Y-%m-%d") or empty string if unsuccessful
    """
    
    # Datetime Info
    # Datetime Info - At the moment this is the only database forced format into a date and must be valid
    event_date = in_event.css(".event-date::attr(datetime)").extract_first()
    if event_date is not None:
        temp_date = dateparser.parse(event_date)
    else:
        #Need to determine best fallback
        return ""
    
    return temp_date.strftime("%Y-%m-%d")

def get_start_time(in_event):
    """Extract show start time from a string
    
    Args:
        in_event (scrapy.http.response.html.HtmlResponse): The html response for the single event from bar 303 website
    
    Returns:
        str: Start Time or None if unsuccessful
    """
    
    temp_time = in_event.css(".event-time-12hr-start::text").extract_first()
    if temp_time is not None:
        temp_time = temp_time.strip()
        #Bar 303 format can be 'Time: 0:00 pm - 0:00 pm'
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