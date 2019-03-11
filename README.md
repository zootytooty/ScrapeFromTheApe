# ScrapeFromTheApe

Melbourne jazz gig scraper. The scaper is designed for:

**Implemented**
* [Jazzlab](https://jazzlab.club/)
* [Paris Cat](http://pariscat.com.au/)
* [Birds Basement](https://birdsbasement.com)

**To-Do**

* [Uptown](https://www.uptownjazzcafe.com)




## Running the scraper

First, ensure all libraries are installed:
```bash
cd ScrapeFromTheApe
pip install requirements.txt
```

To run a single spider, run:

```bash
scrapy crawl jazzlab
```

To run all spiders, run:
```bash
python crawl_all.py
```