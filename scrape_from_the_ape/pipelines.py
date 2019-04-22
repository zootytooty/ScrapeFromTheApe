import dateparser
import requests

class ScrapeFromTheApePipeline(object):

    def __init__(self):
        self.all_gigs = []


    def close_spider(self, spider):

        response = requests.post(url = "https://4xo55t0ma9.execute-api.ap-southeast-2.amazonaws.com/dev/gigmanagement/addgigs", 
                                json = self.all_gigs)

    
    def process_item(self, item, spider):

        # Capture item to store once all scraping is complete
        # noting they must be dictionaries in order to send to the API
        self.all_gigs.append(dict(item))
    
        return item
