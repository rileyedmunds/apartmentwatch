import pandas as pd
import pylab
import requests
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
one_apt = apts[10]
# print(one_apt.prettify())
# size = one_apt.findAll(attrs={'class': 'housing'})[0].text
size = one_apt.findAll(attrs={'class' : 'housing'})[0].text
print(size)
