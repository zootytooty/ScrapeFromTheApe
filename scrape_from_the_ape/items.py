# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapeFromTheApeItem(scrapy.Item):
    
    venue = scrapy.Field()
    title = scrapy.Field()
    music_starts = scrapy.Field()
    doors_open = scrapy.Field()
    date = scrapy.Field()
    price = scrapy.Field()
    desc = scrapy.Field()
    url = scrapy.Field()
    image_url = scrapy.Field()