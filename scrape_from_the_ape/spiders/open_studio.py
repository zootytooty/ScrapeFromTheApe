# -*- coding: utf-8 -*-
import scrapy
from scrape_from_the_ape.items import *
import dateparser

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
	    
        # Datetime Info
        # expected format from Open studio is in the correct style, but the parser will help verify it
        event_date = response.css(".tribe-events-start-date::attr(title)").extract_first()
        event_date1 = response.css(".tribe-events-start-datetime::attr(title)").extract_first()
        event_date2 = response.css(".tribe-events-start-date::text").extract_first()
        event_date3 = response.css(".tribe-events-start-datetime::text").extract_first()
        if event_date is not None:
            temp_date = dateparser.parse(event_date)
        elif event_date2 is not None:
            #Try to use the contents of the element rather than the attribute title (unfortunately this is problematic as the year isn't clear, but we can guess that)
            #Need to catch the error here as well if the selector is empty/non-existant
            temp_date = dateparser.parse(event_date2, settings={'PREFER_DATES_FROM': 'future'})
        elif event_date1 is not None:
            temp_date = dateparser.parse(event_date1)
        elif event_date3 is not None:
            temp_date = dateparser.parse(event_date3, settings={'PREFER_DATES_FROM': 'future'})
        else:
            #Need to determine best fallback
            temp_date = dateparser.parse("Now")
        
        date = temp_date.strftime("%Y-%m-%d")    
        
        temp_time = response.css(".tribe-events-start-time::text").extract_first()
        if temp_time is not None:
            temp_time = temp_time.strip()
            #Open Studio format is 'Time: 0:00 pm - 0:00 pm'
	        #Strip the front 'Time:' prefix if its there
            if temp_time[:5] == 'Time:':
            	temp_time = temp_time[5:].strip()
            #Now seperate the time range if its there
            temp_time = temp_time.split('-')[0].strip()
        else :
            temp_time = ""

        gig['date'] = date

        # Open venu so doors open 19:00 on weekday and 13:30 on weekends according to bar facebook page
        if temp_date.weekday() >=5:
            gig['doors_open'] = "7:00 pm"
        else:
            gig['doors_open'] = "1:30 pm"

        gig['music_starts'] = temp_time
        
        #Clean up the markup, there are lots of empty divs shoving a \n into our description
        temp_descrip = response.css(".tribe-events-single-event-description ::text").extract()
        descr = ""
        for str_x in temp_descrip:
            temp_clean_str = str_x.strip('\n').strip('\t')
            if len(temp_clean_str) != 0:
        	    descr = "".join([descr,str_x,'\n'])
        	
        #Clean up the price
        temp_price = response.css(".tribe-events-event-cost2::text").extract_first()
        if temp_price is not None:
            temp_price = temp_price.split()
            if len(temp_price) > 1:
                temp_price = temp_price[1]
            else:
                temp_price = temp_price[0]
        else:
        	temp_price = ""

        # Show details
        gig['title'] = response.css(".tribe-events-single-event-title::text").extract_first()
        gig['price'] = temp_price
        gig['desc'] = descr
        gig['url'] = response.request.url
        gig['image_url'] = response.css("div#tribe-events-single-event-meta-wrapper img::attr(src)").extract_first()

        gig['venue'] = self.name
        
        yield gig