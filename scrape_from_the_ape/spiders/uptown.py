# -*- coding: utf-8 -*-
import scrapy
from scrape_from_the_ape.items import *
import re
import dateparser
import datetime
import requests

# Utility Fns
import scrape_from_the_ape.utils.datetime_helpers as dth
import scrape_from_the_ape.utils.utils as ut


class UptownCafe(scrapy.Spider):
    name = 'uptown_cafe'

    start_urls = ['https://www.uptownjazzcafe.com']
    
    # The post fix url locations for the complete gig guide
    month_url = ['jan.php','feb.php','mar.php','apr.php','may.php','jun.php','jul.php','aug.php','sep.php','oct.php','nov.php','dec.php']
    base_url = 'https://www.uptownjazzcafe.com'
    
    # Used to check for duplicate events, but probably not needed at this scope level, was intended to help make this spider asynchronous, and maybe that could be a future thing to ensure we don't lock the spiders with a single parse call.
    dates_time_done = [] 
    
    def parse(self, response):
        gigs = [];
	        
        # Downloads HTML & creates a scrapy object for each month from this month
        #Cycle through the year to the end
        for month in self.month_url[datetime.date.today().month-1:]:
            site_url = "/".join([self.base_url,month])
            nextresponse = scrapy.http.HtmlResponse(url = "Up Gig", body=(requests.get(site_url)).text, encoding='utf-8')
            showsul = nextresponse.css('.cushycms#week1>ul>li')
            if showsul:
                for show in showsul:
                    date = show.css('span::text').extract_first()
                    if date:
                        date = dateparser.parse(date[0])
                    if date:
                        title = show.css('::text').extract()
                        item = ScrapeFromTheApeItem()
                        
                        if len(title) > 1:
                            title = "".join(title[1:])
                        else:
                            title = title[0]

                        item['title'] = title
                        item['performance_date'] = date.strftime("%Y-%m-%d")
                        item['description'] = ""
                        item['price'] = ut.parse_price("")
                        item['image_url'] = ""
                        
                        # Best guess given the lack of information on the website                       
                        item['music_starts'] = dth.get_timestamp("8:30 pm")
                        item['doors_open'] = dth.get_timestamp("8:00 pm")
                        item['url'] = site_url
                        item['venue'] = self.name
                        self.dates_time_done.append(''.join([item['performance_date'],item['music_starts']]))
                        gigs.append(item)
            
        shows = response.css('.gig-wrap')
        for show in shows:
            duplicate_entry_found = False
            item = ScrapeFromTheApeItem()
            
            # To get the title, date and time we need to search the h2 tag manually, for some reason the h2 element cannot be selected, so I have to do the reverse of it
            #h2 = show.css('h2 ::text').extract();
            h2 = show.css('*:not(.gig-info-wrap) > p ::text').extract()
            
            # Put it all together
            descr = ""
            for str_x in h2:
                temp_clean_str = re.sub('\n+|([ \t]*\r\n)+','\n',str_x).strip()
                if len(temp_clean_str) != 0:
                    descr = "".join([descr,temp_clean_str,'\n'])
            
            datefound = False
            timefound = False
            # Test if there's a date or time
            time = re.search('\d+[: ]+\d+[ ]*(am|pm)*',descr,re.IGNORECASE)
            date = re.search('\d+(st|rd|th)*[ ]*(Ja|Fe|Ma|Ap|Ma|Ju|Au|Se|Oc|No|De)[^ \r\n\-]*',descr,re.IGNORECASE)
            #date = None
            #time = None
            if date:
                dateFound = True
                date = dateparser.parse(date[0])
                date = date.strftime("%Y-%m-%d")
                item['performance_date'] = date
            else:
                item['performance_date'] = None
            if time:
                # Should parse the time here!
                timeFound = True
                time = dateparser.parse(time[0])
                item['music_starts'] = dth.get_timestamp(time.strftime("%-I:%M %p"))
            else:
                # This place always starts music at 8:30, but often there are two sets of things, so this needs attention
                item['music_starts'] = dth.get_timestamp("8:30 pm")
            
            #Check for a duplicate and store index for later
            
            index_of_duplicate = 0
            try:
                index_of_duplicate = self.dates_time_done.index(''.join([item['performance_date'],item['music_starts']]))
                duplicate_entry_found = True
            except ValueError:
                duplicate_entry_found = False
                
            
            # Best guess given the lack of information on the website
            item['doors_open'] = dth.get_timestamp("8:00 pm")
            
            # Now strip the date and time from the h2 elements and hopefully we are left with a title
            descr = re.sub('\d+[:. ]+\d+[ ]*(am|pm)*','',descr,flags=re.IGNORECASE)
            descr = re.sub('\d+(st|rd|th)*[ ]*(Ja|Fe|Ma|Ap|Ma|Ju|Au|Se|Oc|No|De)[^ .\-]*','',descr,flags=re.IGNORECASE)
            descr = re.sub('saturday|sunday|monday|tuesday|wednesday|thursday|friday','',descr,flags=re.IGNORECASE)
            #THere's definately a better way to do this, i.e. use re.search and strip all stupid characters at the start of a title
            descr = descr.strip().strip('-').strip()
            item['title'] = descr
            
            # The Read More implementation is pointless on this site, so ignore it
            price = ""
            descr_html = show.css('.gig-info-wrap p::text').extract()
            descr = ""
            for str_x in descr_html:
                temp_clean_str = re.sub('\n+|([ \t]*\r\n)+','\n',str_x).strip()
                if len(temp_clean_str) != 0:
                    descr = "".join([descr,temp_clean_str,'\n'])
            
            # First attempt, lets find a $ symbol and pull the sentance or line its on as the price
            price = re.findall("[^\n.|\-,]*[$][ ]*\d+[^\n.|\-,]*",descr)
            if not price:
                # Ok lets see if its a donation or free
                price = re.search("free|donation",descr,re.I)
                if price:
                    price = price[0]
                else:
                    # Ok we cannot determine the price
                    price = ""
            else:
                price = ". ".join(x.strip() for x in price)

            price = ut.parse_price(price)

            
            img = show.css('.gig-info-wrap img::attr(src)').extract_first()
            if not img:
                img = ''
            else:
                img = "{}/{}".format(self.base_url,img)
            site_url = response.request.url
            
            item['description'] = descr
            item['price'] = price
            item['image_url'] = img
            item['url'] = site_url
            item['venue'] = self.name
            
            if duplicate_entry_found:
                gigs[index_of_duplicate] = item
            else:
                #record the date so no duplicates occur
                self.dates_time_done.append(''.join([item['performance_date'],item['music_starts']]))
                gigs.append(item)
        
        for item in gigs:
            yield item
