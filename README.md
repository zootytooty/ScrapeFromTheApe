# ScrapeFromTheApe

Melbourne jazz gig scraper. The scaper is designed for:

### Implemented & Working
* [Paris Cat](http://pariscat.com.au/)
* [Jazzlab](https://jazzlab.club/)
* [Birds Basement](https://birdsbasement.com)
* [Brunswick Green](http://www.thebrunswickgreen.com)
* [Uptown](https://www.uptownjazzcafe.com)
* [The Moldy Fig](https://themoldyfig.com.au/)


### Implemented & Not Working
* [Open Studio](http://openstudio.net.au)
* [Bar 303](http://303.net.au)

### To-Do

* [The Fitzroy Pinnacle](https://www.fitzroypinnacle.com.au) - PDF
* [The Rooks Return](http://therooksreturn.com.au) - Facebook Feed (seems empty for gigs)
* [Arts Centre](https://artscentremelbourne.com.au) - Need a genre filter for jazz/blues/funk
* [The Night Cat](https://www.thenightcat.com.au)
* [Dizzy Jazz Club](https://www.dizzys.com.au) - Once it reopens again
* [Lido Jazz Room](https://www.lidocinemas.com.au)
* [Ruby's Music Room](http://www.rubysmusicroom.com) - Relocating & might be dead
* [Vamos](https://www.vamos.net.au)
* [Speakeasy HQ](https://speakeasy-hq.com) - Mix of genres
* [Tranist Rooftop Bar](https://tranistrooftopbar.com.au) - Sometimes not jazz
* [Claypots Seafood Bar](http://claypots.com.au) - Website down, only facebook at the moment
* [Rainbow Hotel](http://therainbow.com.au)
* [La Niche Cafe](https://lanichefitzroy.com)
* New version of [Jaspers](https://www.instagram.com/jaspersclub/?hl=en) once it opens
* [Candlelight Series](https://feverup.com/melbourne/search?q=candlelight)
* [Lebowskis Music](http://www.lebowskismusic.com/)
* ~[Spotted Mallard](https://www.spottedmallard.com)~
  * Unfortunately they're dead


### Something Missing?
Notice a venue missing that should be on the list? Create an issue & we'll endeavour to add it in. Better yet, raise a PR with the scaper :)


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

## Deployment

The API is managed via the [serverless framework](https://www.serverless.com/), using an AWS backend. To deploy, install the dependencies then run deploy using your desired AWS profile.

```bash
npm install
sls deploy --aws-profile <profile-name>
```
