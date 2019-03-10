#%%
import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
import pandas as pd


#%%
# Get Uptown Gig Guide HTML
uptown_url = "https://www.uptownjazzcafe.com/mar.php"
uptown = requests.get(uptown_url)
soup = bs(uptown.text, 'html.parser')

# Get section contains actual gigs & identify the gig elements
all_gigs = bs(str(soup.find('ul', {'id': 'week1'})), 'html.parser')
gig_list = all_gigs.find_all('li')


#%%
def uptown_gigs(show_date, artist):
    return{
        'show_date': datetime.strptime(show_date, "%A %d, %B %Y"),
        'artist': artist
    }



#%%
# Iterate through & capture each top-level gig

current_month_year = "March 2019"  # This should be smarter
all_gigs = []


for gig in gig_list:

    if len(gig.contents) > 1:
        # Extract Artist
        artist = gig.contents[1]    

        # Extract Gig Date
        scrape_date = gig.find(text=True)
        full_date = "{}, {}".format(scrape_date, month)

        # Capture
        all_gigs.append(uptown_gigs(full_date, artist))


pd.DataFrame(all_gigs)
