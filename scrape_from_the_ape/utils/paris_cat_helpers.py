"""
Title: Paris Cat Helpers
Desc:  A collection of utility functions to organise parsing Paris Cat
"""

import requests
from datetime import datetime
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

    # Generally titla & start time are provided in a single string split by either "//" or "/"
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

    # Get long description
    desc = description_getter(gig['productId'],
                   gig['dateIndex'],
                   title,
                   gig['description']
                   )

    # Instantiate Return Object
    item = ScrapeFromTheApeItem()

    # Fill
    item['title'] = title
    item['music_starts'] = start_time
    item['doors_open'] = gig['availabilityDescriptionOverride'].replace('doors open ', '')
    item['date'] = datetime.strptime(str(gig['dateIndex']), "%Y%m%d").strftime("%Y-%m-%d")
    item['price'] = gig['totalCostDescription']
    item['desc'] = desc
    item['url'] = gig['detailsUrl']
    item['image_url'] = gig['imageUrl']

    return item


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


