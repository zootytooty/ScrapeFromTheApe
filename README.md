# ScrapeFromTheApe

Melbourne jazz gig scraper. The scaper is designed for:

**Implemented**
* [Jazzlab](https://jazzlab.club/)
* [Paris Cat](http://pariscat.com.au/)
* [Birds Basement](https://birdsbasement.com)
* [Open Studio](http://openstudio.net.au)
* [Bar 303](http://303.net.au)

**To-Do**

* [Uptown](https://www.uptownjazzcafe.com)




## Running the scraper

First, ensure all libraries are installed:
```bash
cd ScrapeFromTheApe
pip install -r requirements.txt
```

To run a single spider, run:

```bash
scrapy crawl jazzlab
```

To run all spiders, run:
```bash
python crawl_all.py
```