import pandas as pd
import pylab
import requests
import numpy as np
from bs4 import BeautifulSoup as bs4

#define up page to scrape:
url_short = 'https://chicago.craigslist.org/search/wcl/apa'
parameters = dict(bedrooms=1, is_furnished=1)
get = requests.get(url_short, params=parameters)

#confirm requests parsed the url correctly
#print(get.url) # print(get.text[:500])

#parse response as HTML using bs4:
html = bs4(get.text, 'html.parser')
# print(html.prettify()[:1000])

#beautiful soup can find all instances of a container:
apts = html.find_all('p', attrs={'class': 'row'})
# print(len(apts))
#note: bs4 prettify prints cleanly as XML with each tag on its own line:
one_apt = apts[15]
# print(one_apt.prettify())
# size = one_apt.findAll(attrs={'class': 'housing'})[0].text
size = one_apt.findAll(attrs={'class' : 'housing'})[0].text

#clean and parse size and bedrooms, dealing with case where one is missing
def extract_size_and_brs(size):
    reduced = size.strip('/- ').split(' - ')
    if len(reduced) == 2:
        n_brs = reduced[0].replace('br', '')
        this_size = reduced[1].replace('ft2', '')
    elif 'br' in reduced[0]:
        #there's no footage
        n_brs = reduced[0].replace('br', '')
        this_size = np.nan
    elif 'ft2' in reduced[0]:
        #there's no bedrooms
        n_brs = np.nan
        this_size = reduced[0].replace('ft2','')
    return float(this_size), float(n_brs)

#clean parse time as datetime
def extract_time(input):
    time = input.find('time')['datetime']
    datetime = pd.to_datetime(time)
    return datetime

#clean and parse price as float
def extract_price(input):
    price = input.find('span', {'class': 'price'})
    price_clean = float(price.text.strip('$'))
    return price_clean

#clean and parse price as float
def extract_title(input):
    title = input.find('a', {'class': 'hdrlnk'})
    title_text = title.text
    return title_text


this_size,this_n_brs = extract_size_and_brs(size)
this_time = extract_time(one_apt)
this_price = extract_price(one_apt)
this_title = extract_title(one_apt)

print(this_size)
print(this_n_brs)
print(this_time)
print(this_price)
print(this_title)