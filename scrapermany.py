import pandas as pd
import pylab
import requests
import numpy as np
from bs4 import BeautifulSoup as bs4

# clean and parse size and bedrooms, dealing with case where one is missing
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

#deal with errors in batch price extraction:
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

#clean and parse price as float
def extract_title(input):
    title = input.find('a', {'class': 'hdrlnk'})
    title_text = title.text
    return title_text


# store outcomes in results
results = []

#Note to not request too often => IP ban from Craigslist
search_indices = np.arange(5, 300, 300)
for i in search_indices:
    url = 'https://chicago.craigslist.org/search/wcl/apa'
    resp = requests.get(url, params={'bedrooms': 1, 's': i})
    txt = bs4(resp.text, 'html.parser')
    apts = txt.findAll(attrs={'class': "row"})
    print(apts)

    # Find the size of all listings
    size_text = [rw.findAll(attrs={'class': 'housing'})[0].text
                 for rw in apts]
    print(size_text)

    sizes_brs = [extract_size_and_brs(stxt) for stxt in size_text]
    print(sizes_brs)
    sizes, n_brs = zip(*sizes_brs)  # This unzips into 2 vectors

    # Find the title and link
    title = [rw.find('a', attrs={'class': 'hdrlnk'}).text
             for rw in apts]
    links = [rw.find('a', attrs={'class': 'hdrlnk'})['href']
             for rw in apts]

    # Find the time
    time = [pd.to_datetime(rw.find('time')['datetime']) for rw in apts]
    price = find_prices(apts)

    # populating the dataframe from a dictionary
    data = {'time' : time, 'price': price,
            'size' : list(sizes), 'brs': n_brs,
            'title': title, 'links': links}
    df = pd.DataFrame(data)
    df = df.set_index('time')

    #add the newly created dataframe to the results
    results.append(df)
    print(df.head())

# Finally, concatenate all the results
results = pd.concat(results, axis=0)

#fix types of the numerical columns:
results[['price', 'size', 'brs']] = results[['price', 'size', 'brs']].convert_objects(convert_numeric=True)

