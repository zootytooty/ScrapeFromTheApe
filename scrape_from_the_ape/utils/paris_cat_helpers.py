"""
Title: Paris Cat Helpers
Desc:  A collection of utility functions to organise parsing Paris Cat
"""

import requests
from datetime import datetime
import re
from bs4 import BeautifulSoup as bs
from bs4.element import Tag
from ..items import *


def gig_details(music_starts, doors_open, date, title, price, desc, url, image_url):

    return {
        "music_starts": music_starts,
        "doors_open": doors_open,
        "date": date,
        "title": title,
        "price": price,
        "desc": desc,
        "url": url,
        "image_irl": image_url
    }


def name_splitter(name: str):
    """Extract gig name & start time from string
    
    Args:
        name (str): name item from ParisCat GetStack
    
    Returns:
        str, str: title, start_time
    """

    # Initialise Reponse Variables
    title = None
    start_time = None

    # Generally title & start time are provided in a single string split by either "//" or "/"
    start_name_split = [x.strip('/').strip() for x in name.split('/',1) if x != '']
    if len(start_name_split) == 2:
        title = start_name_split[1]
        start_time = start_name_split[0]
        
        return start_time, title

    # Some names don't contain a start time & thus are length 1
    elif len(start_name_split) == 1:

        title = start_name_split[0]
        start_time = None

    return start_time, title


def pariscat_gig_parser(gig: dict):
    """Orchestrates cleaning & enriching scraped gigs
    
    Args:
        gig (dict): JSON Object from ParisCat GetStack
    
    Returns:
        ScrapeFromTheApeItem: Enriched results
    """

    # Title & start time are provided in a single string split by "//"
    start_time, title = name_splitter(gig['name'])
    if start_time:
        start_time = get_timestamp(start_time)
    # start_time = datetime.strptime(start_time, '%I.%M%p').strftime("%H:%M")

    # Get long description
    desc = description_getter(gig['productId'],
                   gig['dateIndex'],
                   title,
                   gig['description']
                   )

    # Clean up doors open
    doors_open = gig['availabilityDescriptionOverride'].replace('doors open ', '')
    if doors_open:
        doors_open = get_timestamp(doors_open)
    # doors_open = datetime.strptime(doors_open, '%I.%M%p').strftime("%H:%M")

    # Instantiate Return Object
    item = ScrapeFromTheApeItem()

    # Fill
    item['title'] = title
    item['music_starts'] = start_time
    item['doors_open'] = doors_open
    item['performance_date'] = datetime.strptime(str(gig['dateIndex']), "%Y%m%d").strftime("%Y-%m-%d")
    item['price'] = float(gig['totalCostDescription'].replace('$',''))
    item['description'] = desc
    item['url'] = gig['detailsUrl']
    item['image_url'] = gig['imageUrl']

    return item



def time_parser(time):
    """Converts timestamps into a consistent computer usable form.
    Handles timestamps of the format:
        - 1.00PM (or AM)
        - 1:00PM (or AM)
        - 1PM (or AM)
        - 13:00

    Args:
        time (str): Timestamp to be standardised 
    
    Returns:
        str: Timestamp in format HH:MM
    """

    time = time.lower()

    # Idenfiy delimiter 
    raw_time = time.replace('pm','').replace('am','').strip()
    if '.' in time:
        delimiter = '.'
    elif ':' in time:
        delimiter = ':'
    else:
        delimiter = ':'
        raw_time += ':00'

    # Identify whether it's in 12hr or 24hr time
    if 'pm' in time:
        time_to_parse = "{} pm".format(raw_time)
        time_format = "%I{}%M %p".format(delimiter)
        
        clean_time = datetime.strptime(time_to_parse, time_format).strftime("%H:%M")

    elif 'am' in time:
        time_to_parse = "{} am".format(raw_time)
        time_format = "%I{}%M %p".format(delimiter)
        
        clean_time = datetime.strptime(time_to_parse, time_format).strftime("%H:%M")
        
    else:
        clean_time = datetime.strptime(time, "%H:%M").strftime("%H:%M")


    return clean_time


def get_timestamp(time_string):
    """Identified & extracts a timestamp from a string
    
    The currently supported formats are:
        - 01am
        - 1am
        - 12am
        - 12 am
        - 1 am
        - 12:12am
        - 12:12 am
        - 12.12am
        - 12.12 am
    
    Args:
        time_string (str): String that contains a timestamp
    
    Returns:
        str: Timestamp in format HH:MM
    """
    matches = re.findall(r"(\d{0,2}(?:.|:)\d{0,2}\s?(?:AM|PM|pm|am))|(\d{2}(?:.|:)\d{0,2})", time_string)
    matches = matches[0]
    matches = [x.strip() for x in matches if x != '']
    if len(matches) == 1:
        match = matches[0]
        match = time_parser(match)
        return match
    else:
        return None




#********************************************************
## DESCRIPTION HELPERS
#********************************************************

def widget_content(product_id: int, date_index: int):
    """Gets gig details from the product API
    
    Args:
        product_id (int): productId from ParisCat GetStack
        date_index (int): dateIndex from ParisCat GetStack
    
    Returns:
        dict: Product API JSON
    """

    description_url = "https://api.rollerdigital.com/api/products/availabilities/widget"
    headers = {
        'x-api-key': "pariscat"
    }
    query_string = {
        "productId": product_id,
        "startDateIndex": date_index,
        "endDateIndex": date_index
    }

    try:
        desc = requests.get(description_url, headers = headers, params=query_string)
        return desc.json()
    except:
        return None


def text_extraction(desc: str):
    """Extracts text item from description
    
    Args:
        desc (str): Products description
    
    Returns:
        str: Description text
    """

    if isinstance(desc, Tag):
        return desc.text
    else:
        return desc


def description_getter(product_id: int, date_index: int, title: str, raw_short_desc: str):
    """Sources long description, cleans it & returns it
    
    Args:
        product_id (int): productId from ParisCat GetStack
        date_index (int): dateIndex from ParisCat GetStack
        title (str): Extracted gig title
        raw_short_desc (str): description from ParisCat GetStack
    
    Returns:
        str: Long description for the show
    """

    # 1. Get gig page content
    content = widget_content(product_id, date_index)

    # 2. Prepare short description for comparison
    short_desc = bs(raw_short_desc, 'html.parser')
    short_desc = [x.text for x in short_desc.findAll() if x.text != '']

    # 3. Extract text from long description
    long_description = content['products'][0]['description']
    long_desc = bs(long_description, 'html.parser')

    long_desc = [text_extraction(x) for x in long_desc.contents]
    long_desc = [x for x in long_desc if x != '' and
                                         x != title and 
                                         x not in short_desc]

    # Assume there are no spaces between list items
    return ' '.join(long_desc)


