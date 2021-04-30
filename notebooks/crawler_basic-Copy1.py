#!/usr/bin/env python
# coding: utf-8

# # IMAGE CRAWLER

# In[149]:


import requests as req
from bs4 import *
from queue import Queue
import logging
import os
import uuid
from threading import Thread
import re
# from flask import abort, Flask, request, jsonify


# In[ ]:





# In[150]:


#url = "https://www.airbnb.co.uk/s/Ljubljana--Slovenia/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&query=Ljubljana%2C%20Slovenia&place_id=ChIJ0YaYlvUxZUcRIOw_ghz4AAQ&checkin=2020-11-01&checkout=2020-11-08&source=structured_search_input_header&search_type=autocomplete_click"
url2 = "http://4chan.org/"


# In[160]:


logging.basicConfig(format='scraper - %(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
# app = Flask(__name__)
tasks_results = {}


# In[161]:


class Tasks:
    """Class for storing info for every task and return info and results"""

    def __init__(self, task_uuid, queue_urls):
        """
        Init new class copy
        :param task_uuid: UUID of task
        :param queue_urls: queue URLs
        """
        from time import time
        self.found_urls = {}
        self.urls_done = {}
        self.time_takes = None
        self.time_start = time()
        self.task_uuid = task_uuid
        for url in queue_urls:
            self.urls_done[url] = False
            self.found_urls[url] = []

    def prepare_url(self, src_url, url):
        """
        Formating URL
        :param src_url: root URL
        :param url: URL scraped
        :return: formated URL
        """
        import re
        if re.match(r'^[/]{2}.*', url):
            return f'http:{url}'
        elif re.match(r'^/\w+.*', url):
            return f'{src_url}{url}'
        elif not re.match(r'^http.*', url):
            return f'{src_url}/{url}'
        return url

    def _add_url(self, src_url, url):
        """
        Check if url fit info that needed, add it to results
        :param src_url: main URL
        :param url: URL scraped
        :return: None
        """
        url_needed = False
        for pat in ['.gif', '.jpg', '.png']:
            if pat in url:
                url_needed = True
                break
        if url_needed:
            if url not in self.found_urls[src_url]:
                self.found_urls[src_url].append(url)

    def add_res(self, src_url, urls):
        """
        Processing with scraped URL
        :param src_url: Main URL
        :param urls: URL scraped
        :return:
        """
        if isinstance(urls, str):
            self._add_url(src_url, urls)
        else:
            for url in urls:
                self._add_url(src_url, url)

    def finished(self, url):
        """
        Set URL as finished to scrape
        :param url: Main URL
        :return:
        """
        from time import time
        self.urls_done[url] = True
        self.time_takes = time() - self.time_start
        logging.info(f'{self.task_uuid} Took {self.time_takes}')

    def status(self):
        """
        Return JSON status
        :return:
        """
        return {"completed": sum(self.urls_done.values()),
                "inprogress": len(self.urls_done.values()) - sum(self.urls_done.values())}

    def __repr__(self):
        return str(self.status())


# In[162]:


task = Tasks(task_id, url_list)
tasks_results[task_id] = task


# In[124]:


def prepare_url(src_url, url):
    import re
    if re.match(r'^[/]{2}.*', url):
        return f'http:{url}'
    elif re.match(r'^/\w+.*', url):
        return f'{src_url}{url}'
    elif not re.match(r'^http.*', url):
        return f'{src_url}/{url}'
    return url


# In[137]:


found_urls = {}


# In[142]:


def _add_url(src_url, url):
    url_needed = False
    for pat in ['.gif', '.jpg', '.png']:
        if pat in url:
            url_needed = True
            break
    if url_needed:
        if url not in found_urls[src_url]:
            found_urls[src_url].append(url)


# In[143]:


def add_res(src_url, urls):
    if isinstance(urls, str):
        _add_url(src_url, urls)
    else:
        for url in urls:
            _add_url(src_url, url)


# In[140]:


## function to get img links
def parse_url(src_url, url, deep_lv = 1):
    ## req will send the request to this link and get the data in text format from this link webpage
    request = req.get(url)
    ## this will change text into html format
    soup = BeautifulSoup(request.text, "html.parser")
    hrefs = soup.find_all(href=True)
    ## grab all img links and append into links list
    images = soup.find_all('img')
    add_res(src_url, [prepare_url(url, link["src"]) for link in images])
    
    if deep_lv > 0:
        for href in hrefs:
            parse_url(src_url, prepare_url(url, href["href"]), deep_lv=deep_lv - 1)
        
        
    return links
    


# In[141]:


links = parse_url(url2, url2)
links


# In[121]:


href_links = {}
src_url = url2
for href in hrefs:
    href_links[src_url] = parse_url(src_url, prepare_url(url, href["href"]) )
     
href_links


# In[122]:


for href in hrefs:
    a, b = parse_url(url2, prepare_url(src_url, href["href"]))
    print(a)


# In[45]:


parse_url('http://boards.4channel.org/a/')


# In[ ]:


## function to get img links
def parse_url(src_url, url, deep_lv=1):
    ## req will send the request to this link and get the data in text format from this link webpage
    request = req.get(url)
    ## this will change text into html format
    soup = BeautifulSoup(request.text, "html.parser")
    hrefs = soup.find_all(href=True)
    ## grab all img links and append into links list
    images = soup.find_all('img')
    links = [prepare_url(url, link["src"]) for link in images]
    
    if deep_lv > 0:
        for href in hrefs:
            parse_url(src_url, prepare_url(url, href["href"]), deep_lv = deep_lv-1)
        
    return links
    

