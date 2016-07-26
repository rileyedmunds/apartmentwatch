import pandas as pd
import pylab
import requests
import numpy as np
from bs4 import BeautifulSoup as bs4
import string
import time
from twilio.rest import TwilioRestClient
import matplotlib as plt


# ----------------vital functions------------------------

#sending message with specified body
def send_message(message_content):
    # setting up twilio (importing keys from file for public repo security)
    file = open("/Users/rileyedmunds/credentials/twilio", 'r')
    ACCOUNT_SID = file.readline().split()[2]
    AUTH_TOKEN = file.readline().split()[2]
    TWILIO_NUMBER = file.readline().split()[2]
    MY_NUMBER = file.readline().split()[2]

    #sending message
    client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)
    client.messages.create(
        to= MY_NUMBER,
        from_= TWILIO_NUMBER,
        body= message_content
    )

# -------------------------------------------------------

# defining the url and a query we want to post
base_url = 'https://chicago.craigslist.org/'
url = base_url + 'search/wcl/apa?s=5&bedrooms=1'

link_list = []  # storing the data here
link_list_send = []  # list of links to be sent
send_list = []  # what will actually be sent

#avoid all output from the first run:
first_run = True

# Careful with this...too many queries == your IP gets banned temporarily
while True:
    resp = requests.get(url)
    txt = bs4(resp.text, 'html.parser')
    apts = txt.findAll(attrs={'class': "row"})

    # We're just going to pull the title and link
    for apt in apts:
        title = apt.find_all('a', attrs={'class': 'hdrlnk'})[0]
        use_chars = string.ascii_letters + \
                    ''.join([str(i) for i in range(10)]) + \
                    ' /\.'
        name = ''.join([i for i in title.text if i in use_chars])
        link = title.attrs['href']
        if link not in link_list and link not in link_list_send and not first_run:
            print('Found new listing')
            link_list_send.append(link)
            send_list.append(name + '  -  ' + base_url + link)
            print(name + base_url + link)

    # Flush the cache if we've found new entries
    if len(link_list_send) > 0:
        print('Sending mail!')
        msg = '\n'.join(send_list)
        m = email.message.Message()
        m.set_payload(msg)
        gm.send(m, ['recipient_email@mydomain.com'])
        link_list += link_list_send
        link_list_send = []
        send_list = []

    # sleeping so craigslist doesn't ban my IP
    sleep_duration = np.random.randint(5, 10) #60 to 120 seconds
    time.sleep(sleep_duration)