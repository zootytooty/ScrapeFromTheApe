"""
Title: Jazzlab Helpers
Desc:  A collection of utility functions to organise parsing Jazzlab
"""

import requests
from datetime import datetime
import re
from bs4 import BeautifulSoup as bs
from bs4.element import Tag
import dateparser
from ..items import *

# Utility Fns
import scrape_from_the_ape.utils.datetime_helpers as dth
import scrape_from_the_ape.utils.utils as ut



def jazzlab_gig_parser(div, url, venue = 'jazzlab'):

    gig = ScrapeFromTheApeItem()

    # Datetime Info
    date = "{}-{}-{}".format(div.css(".eb-event-date-year::text").extract_first().strip(),
                            div.css(".eb-event-date-month::text").extract_first().strip(),
                            div.css(".eb-event-date-day::text").extract_first().strip()
                        )
    gig['performance_date'] = dateparser.parse(date).strftime("%Y-%m-%d")

    times = div.css(".eb-time::text").extract()
    gig['doors_open'] = dth.get_timestamp(times[0])
    
    if len(times) > 1:
        gig['music_starts'] = dth.get_timestamp(times[1])
    else:
        gig['music_starts'] = None

    # Show details
    gig['title'] = div.css(".eb-event-title span[itemprop*='name']::text").extract_first()
    gig['price'] = ut.parse_price(div.css(".eb-individual-price::text").extract_first())
    gig['description'] = ' '.join([x for x in div.css(".eb-description-details p::text").extract()])
    gig['url'] = "{}{}".format(url, div.css(".eb-event-title::attr(href)").extract_first())
    gig['image_url'] = "{}{}".format(url, div.css(".eb-modal::attr(href)").extract_first())

    gig['venue'] = venue

    return gig




