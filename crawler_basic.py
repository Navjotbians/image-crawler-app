#!/usr/bin/env python
# coding: utf-8

# # IMAGE CRAWLER

# In[113]:


import requests as req
from bs4 import *


# In[114]:


url = "https://www.airbnb.co.uk/s/Ljubljana--Slovenia/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&query=Ljubljana%2C%20Slovenia&place_id=ChIJ0YaYlvUxZUcRIOw_ghz4AAQ&checkin=2020-11-01&checkout=2020-11-08&source=structured_search_input_header&search_type=autocomplete_click"
url2 = "http://4chan.org/"


# In[115]:


url3 = '//s.4cdn.org/image/fp/logo-transparent.png'
def prepare_url(url3):
    import re
    if re.match(r'^[\/]{2}.*', url3):
        return f'http:{url3}'
    elif re.match(r'^\/\w+.*', url3):
        return f'{url3}'
    return url3


# In[116]:


## function to get img links
def parse_url(url):
    ## req will send the request to this link and get the data in text format from this link webpage
    request = req.get(url)
    ## this will change text into html format
    soup = BeautifulSoup(request.text, "html.parser")
    hrefs = soup.find_all(href=True)
    ## grab all img links and append into links list
    images = soup.find_all('img')
    links = [prepare_url(link["src"]) for link in images]
    return links, hrefs
    


# In[117]:


links, hrefs = parse_url(url2)
links


# In[118]:


href_links = []
for href in hrefs:
    href_links.append(prepare_url(href["href"]))
href_links


# In[ ]:




