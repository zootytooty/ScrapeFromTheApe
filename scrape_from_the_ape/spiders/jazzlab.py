# -*- coding: utf-8 -*-
import scrapy
from scrape_from_the_ape.items import *

class JazzlabSpider(scrapy.Spider):
    name = 'jazzlab'
    base_url = 'https://jazzlab.club'
    results_per_page = 12
    start_urls = []

    num_pages = 5
    for page in range(0, (num_pages * results_per_page + 1), results_per_page):
        start_urls.append(f'{base_url}/?layout=timeline&start={page}')


    custom_settings={ 'FEED_URI': "jazzlab.json",
                       'FEED_FORMAT': 'json'}


    def parse(self, response):
        divs = response.css(".eb-category-1")
        
        for div in divs:

            gig = ScrapeFromTheApeItem()

            # Datetime Info
            date = "{}-{}-{}".format(div.css(".eb-event-date-year::text").extract_first().strip(),
                                     div.css(".eb-event-date-month::text").extract_first().strip(),
                                     div.css(".eb-event-date-day::text").extract_first().strip()
                                )
            gig['date'] = date

            times = div.css(".eb-time::text").extract()
            gig['doors_open'] = times[0]
            if len(times) > 1:
                gig['music_starts'] = times[1]

            # Show details
            gig['title'] = div.css(".eb-event-title span[itemprop*='name']::text").extract_first()
            gig['price'] = div.css(".eb-individual-price::text").extract_first()
            gig['desc'] = ' '.join([x for x in div.css(".eb-description-details p::text").extract()])
            gig['url'] = "{}{}".format(self.base_url, div.css(".eb-event-title::attr(href)").extract_first())
            gig['image_url'] = "{}{}".format(self.base_url, div.css(".eb-modal::attr(href)").extract_first())


            yield gig