# -*- coding: utf-8 -*-
import scrapy
import json
from datetime import datetime
from scrape_from_the_ape.utils.paris_cat_helper import *


class ParisCatSpider(scrapy.Spider):
    name = 'paris_cat'

    custom_settings={ 'FEED_URI': "paris_cat.json",
                       'FEED_FORMAT': 'json'}


    def start_requests(self):

        # Generate URL
        todays_date = datetime.now().strftime("%d%m%Y")
        url = "http://api.rollerdigital.com/v1/products/GetStack?token=pariscat&date={}&days=90".format(todays_date)
    
        # Create Request
        headers = {
            'accept': "application/json, text/javascript, */*; q=0.01"
            }

        yield scrapy.http.Request(url = url, headers = headers)


    def parse(self, response):

        json_response = json.loads(response.body_as_unicode())
        for item in json_response:
            gig = pariscat_gig_parser(item)
            yield(gig)

        