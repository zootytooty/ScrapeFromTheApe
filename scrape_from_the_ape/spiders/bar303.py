# -*- coding: utf-8 -*-
import scrapy
from scrape_from_the_ape.items import *
from scrape_from_the_ape.utils.bar303_helpers import *

class Bar303Spider(scrapy.Spider):
    name = 'bar_303'
    start_urls = ['http://303.net.au/gigs-events']
    base_url = 'http://303.net.au'

    def parse(self, response):
        articles = response.css('.eventlist-event--upcoming:not(.eventlist-event--multiday)')
        
        for show in articles:

            gig = ScrapeFromTheApeItem()
            gig = bar303_event_parser(show, self.base_url)
            gig['venue'] = self.name
            yield gig