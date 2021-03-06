# ScrapeFromTheApe

Melbourne jazz gig scraper. The scaper is designed for:

**Implemented**
* [Jazzlab](https://jazzlab.club/)
* [Paris Cat](http://pariscat.com.au/)
* [Birds Basement](https://birdsbasement.com)
* [Open Studio](http://openstudio.net.au)
* [Bar 303](http://303.net.au)
* [Uptown](https://www.uptownjazzcafe.com)
* [Brunswick Green](http://www.thebrunswickgreen.com)
* [Spotted Mallard](https://www.spottedmallard.com)

**To-Do**

* [The Fitzroy Pinnacle](https://www.fitzroypinnacle.com.au) - PDF
* [The Rooks Return](http://therooksreturn.com.au) - Facebook Feed (seems empty for gigs)
* [Arts Centre](https://artscentremelbourne.com.au) - Need a genre filter for jazz/blues/funk
* [The Night Cat](https://www.thenightcat.com.au)
* [Dizzy Jazz Club](https://www.dizzys.com.au) - Once it reopens again
* [Lido Jazz Room](https://www.lidocinemas.com.au)
* [Ruby's Music Room](http://www.rubysmusicroom.com) - Relocating
* [Vamos](https://www.vamos.net.au)
* [Speakeasy HQ](https://speakeasy-hq.com) - Mix of genres
* [Tranist Rooftop Bar](https://tranistrooftopbar.com.au) - Sometimes not jazz
* [Claypots Seafood Bar](http://claypots.com.au) - Website down, only facebook at the moment
* [Rainbow Hotel](http://therainbow.com.au)
* [La Niche Cafe](https://lanichefitzroy.com)


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