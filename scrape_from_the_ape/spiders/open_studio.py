# -*- coding: utf-8 -*-
import scrapy
from scrape_from_the_ape.items import *
from scrape_from_the_ape.utils.open_studio_helpers import *

class OpenStudioSpider(scrapy.Spider):
    name = 'open_studio'
    base_url = 'http://openstudio.net.au/gig_guide/list'
    start_urls = []

    num_pages = 6
    for page in range(1, num_pages):
        start_urls.append(f'{base_url}/?tribe_paged={page}&tribe_event_display=list')

    def parse(self, response):
        divs = response.css(".type-tribe_events")
        
        for div in divs:
            gig = ScrapeFromTheApeItem()
            gig = scrapy.Request(div.css(".tribe-events-read-more::attr(href)").extract_first(), callback=self.parse_event)
            yield gig
            
    def parse_event(self, response):
        gig = ScrapeFromTheApeItem()
        gig = open_studio_event_parser(response)
        gig['venue'] = self.name
        yield gig