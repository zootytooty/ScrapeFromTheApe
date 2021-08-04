"""Crawler Entry Point for Scrape All Sites.

Desc:
    - Executes all spiders sequentially
    - As new spiders are added it will pick them up & run them all with modification
"""

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


def crawl(event: dict, context: object) -> None:
    """Run spiders for all gigs.

    Args:
        event (dict): Lambda event info
        context (object): Methods and properties that provide information about the invocation,
                          function, and execution environment
    """
    settings = get_project_settings()
    process = CrawlerProcess(settings)

    # Add each spider to the crawler process
    # for spider_name in process.spiders.list():
    for spider_name in ["jazzlab", "birds_basement", "paris_cat", "brunswick_green", "uptown_cafe"]:
        print("Running spider: {}".format(spider_name))
        process.crawl(spider_name)

    # Execute all
    process.start()
