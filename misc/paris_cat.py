#%%
import requests
from datetime import datetime
from bs4 import BeautifulSoup as bs
from bs4 import element.Tag


#%%
def gig_details(music_starts, doors_open, date, title, price, desc, url, image_url):

    return {
        "music_starts": music_starts,
        "doors_open": doors_open,
        "date": date,
        "title": title,
        "price": price,
        "desc": desc,
        "url": url,
        "image_irl": image_url
    }

def name_splitter(name):

    # Initialise Reponse Variables
    title = None
    start_time = None

    # Generally titla & start time are provided in a single string split by either "//" or "/"
    start_name_split = [x.strip('/').strip() for x in name.split('/',1) if x != '']

    if len(start_name_split) == 2:
        title = start_name_split[1]
        start_time = start_name_split[0]
        
        return start_time, title

    elif len(start_name_split) == 1:

        title = start_name_split[0]
        start_time = None

    return start_time, title



def pariscat_gig_parser(gig):

    # Title & start time are provided in a single string split by "//"
    start_time, title = name_splitter(gig['name'])

    # Get long description
    desc = description_getter(gig['productId'],
                   gig['dateIndex'],
                   title,
                   gig['description']
                   )


    return gig_details(
        title = title,
        music_starts = start_time,
        doors_open = gig['availabilityDescriptionOverride'].replace('doors open ', ''),
        date = datetime.strptime(str(gig['dateIndex']), "%Y%m%d").strftime("%Y-%m-%d"),
        price = gig['totalCostDescription'],
        desc = desc,
        url = gig['detailsUrl'],
        image_url = gig['imageUrl']
    )




#%%
def widget_content(product_id, date_index):

    description_url = "https://api.rollerdigital.com/api/products/availabilities/widget"
    headers = {
        'x-api-key': "pariscat"
    }
    query_string = {
        "productId": product_id,
        "startDateIndex": date_index,
        "endDateIndex": date_index
    }

    try:
        desc = requests.get(description_url, headers = headers, params=query_string)
        return desc.json()
    except:
        return None


def text_extraction(x):

    if isinstance(x, element.Tag):
        return x.text
    else:
        return x


def description_getter(product_id, date_index, title, raw_short_desc):

    # 1. Get gig page content
    content = widget_content(product_id, date_index)

    # 2. Prepare short description for comparison
    short_desc = bs(raw_short_desc, 'html.parser')
    short_desc = [x.text for x in short_desc.findAll() if x.text != '']

    # 3. Extract text from long description
    long_description = content['products'][0]['description']
    long_desc = bs(long_description, 'html.parser')

    long_desc = [text_extraction(x) for x in long_desc.contents]
    long_desc = [x for x in long_desc if x != '' and
                                         x != title and 
                                         x not in short_desc]

    return ' '.join(long_desc)





#%%
# Get Gigs

url = "http://api.rollerdigital.com/v1/products/GetStack?token=pariscat&date=10032019&days=90"
results = requests.get(url)


#%%
paris_cat_gigs = [pariscat_gig_parser(x) for x in results.json()]