# -*- coding: utf-8 -*-
import scrapy
from scrape_from_the_ape.items import *
from scrape_from_the_ape.utils.spotted_mallard_helpers import *
import logging
import re

class SpottedMallardSpider(scrapy.Spider):
    name = 'spotted_mallard'
    start_urls = ['https://www.spottedmallard.com/events']
    base_url = 'https://www.spottedmallard.com'

    def parse(self, response):
        events_address = response.css('.pc1 iframe::attr(data-src)').extract_first()
        #logging.warning("INFO: Commencing Parsing SM Events:",events_address)
        if events_address:
            #logging.warning("INFO: Parsing SM Event")
            events_response = scrapy.http.HtmlResponse(url = "Spot Gig", body=(requests.get(events_address)).text, encoding='utf-8')
            # now grab the moshtix feed address
            event = events_response.css('script').extract()
            event = "".join(event)
            #logging.warning("".join(["Mosh Full:",event]))
            moshtix_event_feed = re.search("moshtixFeed\.init\(\"(\S+)\"",event).group(1)
            #logging.warning("".join(["Mosh Feed:",moshtix_event_feed]))
            
            mosh_response = scrapy.http.HtmlResponse(url = "Spot Gig", body=(requests.get(moshtix_event_feed)).text, encoding='utf-8')
            mosh_events = mosh_response.xpath("//item").extract()
            
            #if mosh_events:
                #Do something with the events
            #    logging.warning("INFO: Events found")
            #else:
            #    logging.warning("INFO: No Events found")
            
            for show in mosh_events:
    
                #logging.warning("INFO: Parsing SM Event:")
                #logging.warning(show)
                gig = ScrapeFromTheApeItem()
                gig = spotted_mallard_event_parser(show, self.base_url)
                gig['venue'] = self.name
                yield gig