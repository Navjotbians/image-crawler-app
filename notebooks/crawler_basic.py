#!/usr/bin/env python
# coding: utf-8

# # IMAGE CRAWLER

# In[26]:


import requests as req
from bs4 import *


# In[27]:


url = "https://www.airbnb.co.uk/s/Ljubljana--Slovenia/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&query=Ljubljana%2C%20Slovenia&place_id=ChIJ0YaYlvUxZUcRIOw_ghz4AAQ&checkin=2020-11-01&checkout=2020-11-08&source=structured_search_input_header&search_type=autocomplete_click"


# In[28]:


## req will send the request to this link and get the data in text format from this link webpage
request = req.get(url)


# In[29]:


## we have this text format of webpage from req.get now we want to parse it in html format. 
## once we get the html format then only we could get the image links
soup = BeautifulSoup(request.text, "html.parser") ## this will change text into html format
hrefs = soup.find_all(href=True)
images = soup.find_all('img')


# In[30]:


## grab link from all_img_links and append into links list
links = []
for img_link in images:
    links.append(img_link['src'])
links


# In[51]:


## grabbing all the links including the image links
for href in hrefs:
    print(href["href"])


# In[60]:


## function to get img links
def parse_url(url):
    request = req.get(url)
    soup = BeautifulSoup(request.text, "html.parser")
    hrefs = soup.find_all(href=True)
    images = soup.find_all('img')
    links = [link["src"] for link in images]
    return links, hrefs
    


# In[65]:


links, hrefs = parse_url("http://4chan.org/")
links


# In[66]:


href_links = []
for href in hrefs:
    prepare_url(href["href"])
    href_links.append(href["href"])
href_links


# In[67]:


def prepare_url(url):
    import re
    if re.match(r'^[\/]{2}.*', url):
        return f'http:{url}'
    elif re.match(r'^\/\w+.*', url):
        return f'{url}'
    return url


# In[68]:


prepare_url('https://a0.muscache.com/airbnb/static/icons/apple-touch-icon-76x76-3b313d93b1b5823293524b9764352ac9.png')


# In[ ]:




