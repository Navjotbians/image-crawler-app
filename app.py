# coding=utf-8

#  Copyright (c) 2021.
"""
● An application must take the form of a Web API server.
● We expect that the app will take a list of URLs as input and a number of threads,
and return a job ID used to fetch crawling information/results.
● The app should be able to run multiple crawling jobs at the same time.
● We expect to be able to get information/results about a running/finished job
from your application (using its job ID).
● The data extracted will be a list of image URLs (gif, jpg, png) as output.
● The app should crawl the URLs recursively only until the second level
(to avoid a large amount of data): Fetch the images for each given URL and their children.
● By default, the app will crawl using one thread/coroutine, however,
we should be able to specify the number of thread/coroutine to use when creating a new job.
"""
import logging
import os
import uuid
import re
import requests

from threading import Thread
from time import time
from bs4 import BeautifulSoup
from queue import Queue
from flask import abort, Flask, request, jsonify

logging.basicConfig(format='scraper - %(asctime)s - %(name)s - %(threadName)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
app = Flask(__name__)
tasks_results = {}


class Tasks:
    """Class for storing info for every task and return info and results"""

    def __init__(self, task_uuid, queue_urls):
        """
        Init new class copy
        :param task_uuid: UUID of task
        :param queue_urls: queue URLs
        """
        self.found_urls = {}
        self.urls_done = {}
        self.time_takes = None
        self.time_start = time()
        self.task_uuid = task_uuid
        self.time_takes = None
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
        self.urls_done[url] = True
        if all(self.urls_done.values()):
            self.time_takes = time() - self.time_start
            logging.info(f'{self.task_uuid} Took {self.time_takes}')

    def status(self):
        """
        Return JSON status
        :return:
        """
        result = {"completed": sum(self.urls_done.values()),
                  "inprogress": len(self.urls_done.values()) - sum(self.urls_done.values())}
        if self.time_takes:
            result.update({"time_takes": f'{int(self.time_takes)} sec'})
        return result

    def __repr__(self):
        return str(self.status())


def start_scraping(task_id, url_list, threads=1):
    """
    Start scraping process

    :param task_id: UUID of process
    :param url_list: list URLs
    :param threads: How many threads need to run
    :return:
    """
    task = Tasks(task_id, url_list)
    tasks_results[task_id] = task

    def worker_starer(task_queue, task):
        """
        Thread worker scraper

        :param task_queue: queue with URLs for scrape
        :param task: Class where need store information
        :return:
        """

        ua = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0'
        }
        logger.info(f'Start task {task_queue}')

        def parse_url(src_url, url, deep_lv=1):
            """
            Parser specific URL

            :param src_url: main root source URL
            :param url: URL to parse
            :param deep_lv: how deep looking
            :return:
            """
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
            logger.info(f'Start parsing URL: {url}')
            parse_url(url, url)
            task.finished(url)
            task_queue.task_done()

    queue = Queue()
    for x in range(threads):
        worker = Thread(target=worker_starer, name=f"Thread_{x}_{task_id}", args=(queue, task))
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


@app.route('/status/<task_uuid>', methods=['GET'])
def return_status(task_uuid):
    """
    Return status info by UUID
    :param task_uuid: UUID
    :return: JSON ststus
    """
    if task_uuid in tasks_results:
        return jsonify(tasks_results[task_uuid].status())
    else:
        abort(400)


@app.route('/statistics', methods=['GET'])
def return_statistics():
    """
    Return statistics info
    :return: JSON
    """
    info = {'tasks': len(tasks_results.keys()),
            'urls_requseted': sum([len(task.urls_done.keys()) for task_uuid, task in tasks_results.items()]),
            'time_taken': {},
            'tasks_ids': {}}
    for task_uuid, task in tasks_results.items():
        info['tasks_ids'][task_uuid] = sum(len(task.found_urls[key]) for key in task.found_urls.keys())
        info['time_taken'][task_uuid] = '{:.2f}-Seconds'.format(time() - task.time_start)
    return jsonify(info)


@app.route('/result/<task_uuid>', methods=['GET'])
def return_result(task_uuid):
    """
    Return Status for specific UUID
    :param task_uuid:UUID
    :return: JSON
    """
    if task_uuid in tasks_results:
        return jsonify(tasks_results[task_uuid].found_urls)
    else:
        abort(400)


@app.route('/', methods=['POST'])
def get_task():
    """
    Initialize new task , need post JSON
    :return: JSON info about task
    """
    if not request.json:
        abort(400)
    from_post = request.json
    n_threads = 1
    urls = from_post['urls']
    if 'n_threads' in from_post:
        n_threads = int(from_post['n_threads'])
    if not isinstance(urls, list):
        abort(400)
    taks_uuid = str(uuid.uuid1())
    start_scraping(taks_uuid, urls, n_threads)
    result = {"job_id": taks_uuid, "threads": str(n_threads), "urls": urls}
    return jsonify(result)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(threaded=False, host='0.0.0.0', port=port, debug=True)
