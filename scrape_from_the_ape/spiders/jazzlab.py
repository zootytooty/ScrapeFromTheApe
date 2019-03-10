# -*- coding: utf-8 -*-
import scrapy


class JazzlabSpider(scrapy.Spider):
    name = 'jazzlab'
    start_urls = ['https://jazzlab.club//']

    custom_settings={ 'FEED_URI': "jazzlab.json",
                       'FEED_FORMAT': 'json'}


    def parse(self, response):
        divs = response.css(".eb-category-1")
        
        for div in divs:

            gig = dict()

            # Datetime Info
            gig['day'] = div.css(".eb-event-date-day::text").extract_first().strip()
            gig['month'] = div.css(".eb-event-date-month::text").extract_first().strip()
            gig['year'] = div.css(".eb-event-date-year::text").extract_first().strip()

            times = div.css(".eb-time::text").extract()
            gig['doors_open'] = times[0]
            if len(times) > 1:
                gig['music_starts'] = times[1]

            # Show details
            gig['title'] = div.css(".eb-event-title span[itemprop*='name']::text").extract_first()
            gig['price'] = div.css(".eb-individual-price::text").extract_first()
            gig['blurb'] = ' '.join([x for x in div.css(".eb-description-details p::text").extract()])
            gig['url'] = "{}{}".format(self.start_urls[0], div.css(".eb-event-title::attr(href)").extract_first())


            yield gig