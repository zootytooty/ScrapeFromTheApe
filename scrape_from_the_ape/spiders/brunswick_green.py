# -*- coding: utf-8 -*-
import json
import scrapy
from datetime import datetime
from scrape_from_the_ape.items import *
from scrape_from_the_ape.utils.brunswick_green_helpers import *


class BrunswickGreenSpider(scrapy.Spider):
    name = "brunswick_green"

    def start_requests(self):

        # Generate URL
        month = datetime.now().strftime("%m-%Y")
        url = f"{BASE_URL}/api/open/GetItemsByMonth?month={month}&collectionId=59ef037d017db2e4f36ff118&crumb=BS88q3Z3Ue3iMTU4NjE3ODM3OGFlNTNhZjE4ZDdlOTAwZjM0NDk2"

        # Create Request
        headers = {"accept": "application/json, text/javascript, */*; q=0.01"}

        yield scrapy.http.Request(url=url, headers=headers)

    def parse(self, response):

        json_response = json.loads(response.text)
        for item in json_response:
            gig = brunswick_green_event_parser(item)
            gig["venue"] = self.name
            yield (gig)
