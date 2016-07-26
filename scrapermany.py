import pandas as pd
import pylab
import requests
import numpy as np
from bs4 import BeautifulSoup as bs4

# clean and parse size and bedrooms, dealing with case where one is missing
def extract_size_and_brs(input):
    size = input.findAll(attrs={'class': 'housing'})[0].text
    reduced = size.strip('/- ').split(' - ')
    if len(reduced) == 2:
        n_brs = reduced[0].replace('br', '')
        this_size = reduced[1].replace('ft2', '')
    elif 'br' in reduced[0]:
        # there's no footage
        n_brs = reduced[0].replace('br', '')
        this_size = np.nan
    elif 'ft2' in reduced[0]:
        # there's no bedrooms
        n_brs = np.nan
        this_size = reduced[0].replace('ft2', '')
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



results = []

search_indices = np.arange(0, 300, 300)
# search_indices = range(7)
for i in search_indices:
    # define page to scrape:
    url_short = 'https://chicago.craigslist.org/search/{0}/apa'.format('wcl')
    parameters = {'bedrooms' : 1, 's': i}
    get = requests.get(url_short, params=parameters)
    html = bs4(get.text, 'html.parser')
    apts = html.find_all('p', attrs={'class': 'row'})

    #Calculations will run across all entries for each category.

    #size:
    sizes_and_brs = [extract_size_and_brs(txt) for txt in apts]
    sizes, n_brs = zip(*sizes_and_brs)
    sizes, n_brs = list(sizes), list(n_brs)

    #titles
    title = [extract_title(a) for a in apts]
    #links
    links = [a.find('a', attrs={'class': 'hdrlnk'})['href'] for a in apts]
    #time
    time = [extract_time(a) for a in apts]
    #price
    prices = find_prices(apts)


    #ceate DataFrame to store ouput:
    print(type(time))
    print(type(prices))
    print(type(sizes))
    print(type(n_brs))
    print(type(title))
    print(type(links))
    
    data = np.array([time, prices, list(sizes), list(n_brs), title, links])
    column_names = ['time', 'price', 'size', 'brs', 'title', 'link']
    # print(data.T)
    df = pd.DataFrame(data=data.T, index='time', columns=column_names)
    # df = df.set_index('time')
    #append result to dataframe
    results.append(df)


results = pd.concat(results, axis=0)
# results[['price', 'size', 'brs']] = results[['price', 'size', 'brs']].convert_objects(convert_numeric=True)
print(results[:7])