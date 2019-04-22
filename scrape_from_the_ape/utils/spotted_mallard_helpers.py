"""
Title: Spotted Mallard Helpers
Desc: A collection of utility functions to organise parsing of Spotted Mallard
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



def spotted_mallard_event_parser(in_event, base_url : str):
    """Main process to enrich & return gig data
    
    Args:
        in_event (scrapy.http.response.html.HtmlResponse): Individual show html response portion
        base_url (str): The base url to construct any relative links in the content
        
    Returns:
        ScrapeFromTheApeItem: Scrape Item populated with gig data
    """
    
    #Get the event page
    #site_url = in_event.css("a::attr(href)").extract_first()
    # Unfortunately the moshtix xml uses <link> and Xpath and CSS assumes this is in the standard fornat without any content, hence it will not typically work
    site_url = re.search("<link>[ ]*(\S+)",in_event).group(1)
    #in_event.xpath("//link/text()").get()
    fullevent = scrapy.http.HtmlResponse(url = "Spot Gig", body=(requests.get(site_url)).text, encoding='utf-8')

    gig = ScrapeFromTheApeItem()
    descrip_html = parse_event_description(fullevent)
    
    doors_open = calc_open_doors(descrip_html)
    doors_open = dth.get_timestamp(doors_open)

    price = parse_event_cost(fullevent)
    price = ut.parse_price(price)

    music_starts_raw = get_start_time(fullevent)

    gig['performance_date'] = get_event_date(fullevent) 
    gig['doors_open'] = calc_open_doors(descrip_html)
    gig['music_starts'] = dth.get_timestamp(music_starts_raw)
    gig['description'] = descrip_html
    gig['price'] = price
    
    # Need to fix this up, as we probably should use the open hours of the venue if we cannot find doors open time
    if gig['doors_open'] is None:
    	start_hour = int(re.search("\d+",music_starts_raw,re.I)[0])
    	if start_hour > 7:
    		gig['doors_open'] = dth.get_timestamp("7:00 pm")
    	else:
            doors_open = "".join([str(start_hour),":00 pm"])
            gig['doors_open'] = dth.get_timestamp(doors_open)
    
    
    # Get the main image, or an search the description for an alternate if it doesn't exist, squarepsace uses data-src and imageloader from bootstrap to do fancy image loading. This means the src in the thumbnail is non existant on load
    #img = in_event.css(".eventlist-column-thumbnail img::attr(data-src)").extract_first()
    img = fullevent.css(".page_headleftimage img::attr(src)").extract_first()
    if not img:
    	img = ''
    gig['image_url'] = "".join([site_url,img[1:]])
    
    # Show details
    title = fullevent.css("#event-summary-block::attr(data-event-title)").extract_first()
    if title:
        gig['title'] = title
    else:
        gig['title'] = ""
    
    gig['url'] = site_url
    
    
    return gig

def parse_event_cost(in_event):
    """Find and make nice the gig cost from a single event from website
    
    Args:
        in_event (scrapy.http.response.html.HtmlResponse): The html response for the single event from website
    
    Returns:
        str: Event Cost, empty string if cannot find something
    
    """

    # First attempt, lets find a $ symbol and pull the sentance or line its on as the price
    
    prices = in_event.css(".event-ticket-type-list li")
    if prices:
        price_str = ""
        for price in prices:
            ticket_type = price.css(".ticket-type-name::text").extract_first()
            ticket_cost = price.css(".ticket-type-total span::text").extract_first()
            price_str = "".join([ticket_type, ": ", ticket_cost, ", "])
        return price_str[:-2]
    
    # Possible option to find a cost if its not where we expect it to be
    # Sometime the word free is in the title for the spoted mallard
    title = in_event.css("#event-summary-block::attr(data-event-title)").extract_first()
    price = re.findall("[$][ ]*\d+[^\n.|\-,*]*",title)
    if not price:
        # Ok lets see if its a donation or free
        price = re.search("free|donation",title,re.I)
    
        if price:
            price = price[0]
        else:
            # Ok we cannot determine the price
            price = ""
    else:
        price = ". ".join(x.strip() for x in price)
    
    return price

def parse_event_description(in_event):
    """Find and make nice the gig description from a single event from website
    
    Args:
        in_event (scrapy.http.response.html.HtmlResponse): The html response for the single event from website
    
    Returns:
        str: Event Description, maybe an empty string
    
    """
    
    #Clean up the markup, there are lots of empty divs shoving a \n into our description
    descrip_html = in_event.css(".page ::text").extract()
    descr = ""
    for str_x in descrip_html:
        temp_clean_str = str_x.strip('\n').strip('\t')
        if len(temp_clean_str) != 0:
            descr = "".join([descr,str_x,'\n'])
    return descr.strip()


def calc_open_doors(descr: str):
    """Given event description, searches for the time doors open
    
    Args:
        descr (str): Show description to search
    
    Returns:
        str: Doors open time or "" if date is invalid
    """
    
    # Doors open calculate from the description
    #doors_open = re.search("[^\n.|\-,\\/]*doors[^\n.|\-,\\/]*",descr,re.I)
    doors_open_1 = re.search("doors[\s\D]*(\d+:*\d*(am|pm)?)",descr,re.I)
    #doors_open_2 = re.search("\d+:*\d*(am|pm)?[\s\S]*doors",descr,re.I)
    if doors_open_1:
        return doors_open_1.group(1).strip()
    else:
        return None

def get_event_date(in_event):
    """Extract show start time from the event date-time attribute
    
    Args:
        in_event (scrapy.http.response.html.HtmlResponse): The html response for the single event from Brunswick Green website
    
    Returns:
        str: Event Date ("%Y-%m-%d") or empty string if unsuccessful
    """
    
    # Datetime Info
    # Datetime Info - At the moment this is the only database forced format into a date and must be valid
    temp_date = in_event.css("#event-summary-block::attr(data-event-date)").extract_first()
    if temp_date is not None:
        temp_date = dateparser.parse(temp_date)
    else:
        return ""
    return temp_date.strftime("%Y-%m-%d")

def get_start_time(in_event):
    """Extract show start time from the event date-time attribute
    
    Args:
        in_event (scrapy.http.response.html.HtmlResponse): The html response for the single event from website
    
    Returns:
        str: Start Time or None if unsuccessful
    """
    
    temp_time = in_event.css("#event-summary-block::attr(data-event-date)").extract_first()
    if temp_time is not None:
        temp_time = dateparser.parse(temp_time)
        try:
            temp_time = temp_time.strftime("%-I:%M %p")
        except ValueError:
            return None
    else:
        temp_time = None
    
    return temp_time