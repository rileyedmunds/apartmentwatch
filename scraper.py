#SCRAPER: pull craiglist apartment listings into CSV file. Allows for plotting.


import pandas as pd
import pylab
import requests
import numpy as np
from bs4 import BeautifulSoup as bs4
import string
import time
import matplotlib as plt


#-------------vital functions-------------

# cleaning and parsing size and bedrooms, dealing with case where one is missing
def extract_size_and_brs(size):
    split = size.strip('/- ').split(' - ')
    if len(split) == 2:
        n_brs = split[0].replace('br', '')
        this_size = split[1].replace('ft2', '')
    elif 'br' in split[0]:
        # It's the n_bedrooms
        n_brs = split[0].replace('br', '')
        this_size = np.nan
    elif 'ft2' in split[0]:
        # It's the size
        this_size = split[0].replace('ft2', '')
        n_brs = np.nan
    return float(this_size), float(n_brs)

#cleaning and parsing time as datetime
def extract_time(input):
    time = input.find('time')['datetime']
    datetime = pd.to_datetime(time)
    return datetime

#cleaning and parsing price as float
def extract_price(input):
    price = input.find('span', {'class': 'price'})
    price_clean = float(price.text.strip('$'))
    return price_clean

#dealing with errors in batch price extraction:
def find_prices(inputs):
    prices = []
    for a in inputs:
        price = a.find('span', {'class': 'price'})
        if price is not None:
            price = float(price.text.strip('$'))
        else:
            price = np.nan
        prices.append(price)
    return prices

#cleaning and parsing title
def extract_title(input):
    title = input.find('a', {'class': 'hdrlnk'})
    title_text = title.text
    return title_text

#-----------Non-vital functions----------

#plots histogram of prices.
    #NOTE: will only work with matplotlib inline (IPython notebook)
def draw_hist(data):
    e = results.hist('price', bins=np.arange(0, 10000, 100))[0, 0]
    ax.set_title('price vs count', fontsize = 30)
    ax.set_xlabel('Price', fontsize=15)
    ax.set_ylabel('Count', fontsize=15)

#saves file as CSV:
def save_to_file(data):
    # cleaning extraneous characters out:
    charset = string.ascii_letters + \
                ''.join([str(i) for i in range(10)]) + \
                ' /\.'
    results['title'] = results['title'].apply(
        lambda a: ''.join([i for i in a if i in charset]))

    results.to_csv('data/craigslist_results.csv')


# def text_updates:
#----------------------------------------


#storing outcomes here
results = []

#note to not request too often => IP ban from Craigslist
search_indices = np.arange(5, 300, 300)
for i in search_indices:
    url = 'https://chicago.craigslist.org/search/wcl/apa'
    resp = requests.get(url, params={'bedrooms': 1, 's': i})
    txt = bs4(resp.text, 'html.parser')
    print(resp.url)
    apts = txt.findAll(attrs={'class': "row"})
    print(apts)

    # finding the size of all listings
    size_text = [rw.findAll(attrs={'class': 'housing'})[0].text
                 for rw in apts]
    print(size_text)

    sizes_brs = [extract_size_and_brs(stxt) for stxt in size_text]
    print(sizes_brs)
    sizes, n_brs = zip(*sizes_brs)

    # finding the title & link
    title = [rw.find('a', attrs={'class': 'hdrlnk'}).text
             for rw in apts]
    links = [rw.find('a', attrs={'class': 'hdrlnk'})['href']
             for rw in apts]

    # finding the time
    time = [pd.to_datetime(rw.find('time')['datetime']) for rw in apts]
    price = find_prices(apts)

    # populating the dataframe from a dictionary
    data = {'time' : time, 'price': price,
            'size' : list(sizes), 'brs': n_brs,
            'title': title, 'links': links}
    df = pd.DataFrame(data)
    df = df.set_index('time')

    #adding the newly created dataframe to the results
    results.append(df)
    print(df.head())

# concatenating all the results
results = pd.concat(results, axis=0)

#fixing types of the numerical columns:
results[['price', 'size', 'brs']] = results[['price', 'size', 'brs']].convert_objects(convert_numeric=True)
save_to_file(results)





