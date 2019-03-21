# -*- coding: utf-8 -*-
import scrapy
from scrape_from_the_ape.items import *
import re

class Bar303Spider(scrapy.Spider):
    name = 'bar_303'
    start_urls = ['http://303.net.au/gigs-events']
    base_url = 'http://303.net.au'

    def parse(self, response):
        articles = response.css('.eventlist-event--upcoming:not(.eventlist-event--multiday)')
        
        for show in articles:

            gig = ScrapeFromTheApeItem()

            # Datetime Info - At the moment this is the only database forced format into a date and must be valid
            date = show.css(".event-date::attr(datetime)").extract_first()
            if date:
                gig['date'] = date
            else:
                gig['date'] = ""
            
            gig['doors_open'] = ""
            gig['music_starts'] = show.css(".event-time-12hr-start::text").extract_first()
            
            # Get the main image, or an alternate if it doesn't exist
            img = show.css(".eventlist-column-thumbnail img::attr(src)").extract_first()
            if not img:
                img = show.css(".eventlist-description img::attr(src)").extract_first()
                
            descrip_html = show.css(".eventlist-description .sqs-block-html ::text").extract()
            descr = ""
            for str_x in descrip_html:
                temp_clean_str = str_x.strip('\n').strip('\t')
                if len(temp_clean_str) != 0:
                    descr = "".join([descr,str_x,'\n'])
                    
            # Pricing with bar 303 is often stuffed into the description somewhere, or in the index at the front, so either try and match the event to the summary at the top of the page or do a smart search in the description. Given the summary at the top isn't structured particularily well with html elements, lets do the description search
            # First attempt, lets find a $ symbol and pull the sentance of line its on as the price
            price = re.findall("[^\n.|\-,]*[$][ ]*\d+[^\n.|\-,]*",descr)
            if not price:
                price = ""
            else:
                price = ". ".join(x.strip() for x in price)

            # Show details
            title = show.css(".eventlist-title a::text").extract_first()
            if title:
                gig['title'] = title
            else:
                gig['title'] = ""
            
            gig['price'] = price
            gig['desc'] = descr
            
            gig_url = ''.join([self.base_url,show.css(".eventlist-title a::attr(href)").extract_first()])
            if gig_url:
                gig['url'] = gig_url
            else:
                gig['url'] = ""
            
            gig['image_url'] = img
            
            gig['venue'] = self.name
            
            yield gig