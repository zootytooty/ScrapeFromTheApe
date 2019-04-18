# -*- coding: utf-8 -*-
import scrapy
from scrape_from_the_ape.items import *
from scrape_from_the_ape.utils.brunswick_green_helpers import *

class BrunswickGreenSpider(scrapy.Spider):
    name = 'brunswick_green'
    start_urls = ['http://www.thebrunswickgreen.com/gigs-at-the-green']
    base_url = 'http://www.thebrunswickgreen.com'

    def parse(self, response):
        articles = response.css('.eventlist-event--upcoming:not(.eventlist-event--multiday)')
        
        for show in articles:

            gig = ScrapeFromTheApeItem()
            gig = brunswick_green_event_parser(show, self.base_url)
            gig['venue'] = self.name
            yield gig