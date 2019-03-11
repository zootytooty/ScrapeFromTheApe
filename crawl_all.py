"""
Title: Crawl All

Desc:  
    - Executes all spiders sequentially
    - As new spiders are added it will pick them up & run them all with modification
"""

from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess

setting = get_project_settings()
process = CrawlerProcess(setting)

# Add each spider to the crawler process
for spider_name in process.spiders.list():
    print("Running spider: {}".format(spider_name))
    process.crawl(spider_name)

# Execute all
process.start()