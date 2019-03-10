# -*- coding: utf-8 -*-
import scrapy
from scrape_from_the_ape.items import *
from scrape_from_the_ape.utils.birds_basement_helpers import *


class BirdsBasementSpider(scrapy.Spider):
    name = 'birds_basement'

    start_urls = ["https://birdsbasement.com/whats-on"]

    custom_settings={ 'FEED_URI': "birds_basement.json",
                       'FEED_FORMAT': 'json'}


    def parse(self, response):
        
        shows = content_extractor(response)

        # Parse each show
        for show in shows:

            print('')
            print("#### SHOW TITLE ####")
            print(show['title'])
            print("#### SHOW TITLE ####")
            print('')

            gigs = birds_parser(show)

            print(len(gigs))

            # Return each gig object back for scrapy to capture
            for gig in gigs:
                yield gig