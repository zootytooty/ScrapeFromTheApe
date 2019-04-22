# -*- coding: utf-8 -*-
import scrapy
from scrape_from_the_ape.utils.jazzlab_helpers import *
from scrape_from_the_ape.items import *

class JazzlabSpider(scrapy.Spider):
    name = 'jazzlab'
    base_url = 'https://jazzlab.club'
    results_per_page = 12
    start_urls = []

    num_pages = 5
    for page in range(0, (num_pages * results_per_page + 1), results_per_page):
        start_urls.append(f'{base_url}/?layout=timeline&start={page}')

    def parse(self, response):
        divs = response.css(".eb-category-1")
        
        for div in divs:

            gig = jazzlab_gig_parser(div = div, venue = self.name, url = self.base_url)

            yield gig