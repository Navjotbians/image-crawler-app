#!/usr/bin/env python
# coding: utf-8

# # IMAGE CRAWLER

# In[28]:


import requests as req
from bs4 import *
from queue import Queue
import logging
import os
import uuid
from threading import Thread
import re
from flask import abort, Flask, request, jsonify


# In[29]:


#url = "https://www.airbnb.co.uk/s/Ljubljana--Slovenia/homes?tab_id=home_tab&refinement_paths%5B%5D=%2Fhomes&query=Ljubljana%2C%20Slovenia&place_id=ChIJ0YaYlvUxZUcRIOw_ghz4AAQ&checkin=2020-11-01&checkout=2020-11-08&source=structured_search_input_header&search_type=autocomplete_click"
# ["http://4chan.org/","http://golang.org/"]
# url2 = "http://4chan.org/"


# In[30]:


logging.basicConfig(format='scraper - %(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__)
tasks_results = {}


# In[31]:


class Tasks:
    
    def __init__(self, task_uuid, queue_urls):
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
        import re
        if re.match(r'^[/]{2}.*', url):
            return f'http:{url}'
        elif re.match(r'^/\w+.*', url):
            return f'{src_url}{url}'
        elif not re.match(r'^http.*', url):
            return f'{src_url}/{url}'
        return url

    def _add_url(self, src_url, url):
        url_needed = False
        for pat in ['.gif', '.jpg', '.png']:
            if pat in url:
                url_needed = True
                break
        if url_needed:
            if url not in self.found_urls[src_url]:
                self.found_urls[src_url].append(url)

    def add_res(self, src_url, urls):
        if isinstance(urls, str):
            self._add_url(src_url, urls)
        else:
            for url in urls:
                self._add_url(src_url, url)

    def finished(self, url):
        from time import time
        self.urls_done[url] = True
        self.time_takes = time() - self.time_start
        logging.info(f'{self.task_uuid} Took {self.time_takes}')

    def status(self):
        return {"completed": sum(self.urls_done.values()),
                "inprogress": len(self.urls_done.values()) - sum(self.urls_done.values())}

    def __repr__(self):
        return str(self.status())


# In[32]:


def start_scraping(task_id, url_list, threads=1):
    from queue import Queue
    task = Tasks(task_id, url_list)
    tasks_results[task_id] = task

    def worker(task_queue, task):
        import requests
        from bs4 import BeautifulSoup
        ua = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        }

        def parse_url(src_url, url, deep_lv=1):
            try:
                r = requests.get(url, headers=ua)
                soup = BeautifulSoup(r.text, "html.parser")
                hrefs = soup.find_all(href=True)
                images = soup.findAll('img')
                task.add_res(src_url, [task.prepare_url(url, link['src']) for link in images])

                if deep_lv > 0:
                    for href in hrefs:
                        parse_url(src_url, task.prepare_url(url, href['href']), deep_lv=deep_lv - 1)
            except:
                logger.warning(f'Cant go by link {url}')
                pass

        while True:
            url = task_queue.get()
            if url is None:
                break
            parse_url(url, url)
            task.finished(url)
            task_queue.task_done()

    queue = Queue()
    for x in range(threads):
        worker = Thread(target=worker, name=f"{task_id}_{x}", args=(queue, task))
        # Setting daemon to True will let the main thread exit even though the workers are blocking
        worker.daemon = True
        worker.start()
    # Put the tasks into the queue
    for link in url_list:
        logger.info('{} Queueing {}'.format(task_id, link))
        queue.put(link)
    # Add flag break threads
    for x in range(threads):
        queue.put(None)


# In[33]:


@app.route('/status/<task_uuid>', methods=['GET'])
def return_status(task_uuid):
    if task_uuid in tasks_results:
        return jsonify(tasks_results[task_uuid].status())
    else:
        abort(400)


# In[34]:


@app.route('/statistics', methods=['GET'])
def return_statistics():
    info = {'tasks': len(tasks_results.keys()),
            'urls_requseted': sum([len(task.urls_done.keys()) for task_uuid, task in tasks_results.items()]),
            'tasks_ids': {}}
    for task_uuid, task in tasks_results.items():
        info['tasks_ids'][task_uuid] = len(task.urls_done.keys())
    return jsonify(info)


# In[36]:


@app.route('/result/<task_uuid>', methods=['GET'])
def return_result(task_uuid):if task_uuid in tasks_results:
        return jsonify(tasks_results[task_uuid].found_urls)
    else:
        abort(400)


# In[ ]:


@app.route('/', methods=['POST'])
def get_task():
    if not request.json:
        abort(400)
    urls = request.json
    if not isinstance(urls, list):
        abort(400)
    taks_uuid = str(uuid.uuid1())
    thread_n = 1
    start_scraping(taks_uuid, urls, thread_n)
    result = {"job_id": taks_uuid, "threads": str(thread_n), "urls": urls}
    return jsonify(result)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(threaded=False, host='0.0.0.0', port=port)


# In[ ]:





# In[ ]:




