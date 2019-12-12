import logging
import json
import socket

from queue import Queue
from threading import Thread
from urllib.error import HTTPError, URLError
from urllib.request import build_opener, HTTPRedirectHandler

from collections import namedtuple

from matching import WebsiteParser, validate_url

from typing import Text, Dict, Tuple


'''
This file contains the driving code directing which files to match and aggregating the results.
'''

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

NUM_THREADS_IN_POOL = 15
URLInput = namedtuple('URLInput', ['input_num', 'url', 'handles'])


class BasicRedirectHandler(HTTPRedirectHandler):
    def http_error_301(self, req, fp, code, msg, headers):
        result = HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers)
        result.status = code
        return result

    def http_error_302(self, req, fp, code, msg, headers):
        result = HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
        result.status = code
        return result


class ProcesserThread(Thread):

    def __init__(self, queue, result_list):
        Thread.__init__(self)
        self.queue = queue
        self.result_list = result_list

    def run(self):
        while True:
            # Call blocks on queue empty
            input_num, url, _ = self.queue.get()
            valid_url, suggested_url = validate_url(url)
            if not valid_url:
                logging.error(f'failed to validate url: {url}')
                self.queue.task_done()
                continue

            url_opener = build_opener(BasicRedirectHandler())
            # work-around for when sites reject the standard User-Agent generated.
            url_opener.addheaders = [('User-agent', 'Mozilla/5.0')]

            try:
                response = url_opener.open(suggested_url, timeout=3)
                # Write to file instead of in-memory-store to handle more scale,
                # need to handle ordering differently if this is the case.

                # Use multiprocessing in addition to multi-threading if the CPU-bound work grows (Disk IO)
                handles = WebsiteParser().find_handles(response)
                self.result_list.append(URLInput(input_num, url, handles))

            except URLError as error:
                logging.error(f'failed while parsing {url}: {error}')
                if isinstance(error.reason, socket.timeout):
                    logging.info(f'socket timed out for {url}')

            except HTTPError as error:
                logging.error(f'failed while parsing {url}: {error}')
                if error.code == 503:
                    # This is easily mitigated with the Python ``Requests`` external library.
                    logging.info('503 errors are likely due to being identified '
                                 'as non-human traffic, or gated input was given.')

            finally:
                self.queue.task_done()


def scrape_inputs(inputs) -> Text:
    url_queue = Queue()
    results_store: Tuple[int, Dict[Text, Text]] = []

    for _ in range(NUM_THREADS_IN_POOL):
        worker = ProcesserThread(url_queue, results_store)
        # Allow process to terminate without worrying about worker loop
        worker.daemon = True
        worker.start()

    for input_num, input in enumerate(inputs):
        url_queue.put_nowait(URLInput(input_num, input, None))

    url_queue.join()

    # Including additional info to be able to sort them and include original URL information.
    final_result = [item.handles for item in sorted(results_store, key=lambda item: item.input_num)]
    return_value = json.dumps(final_result, indent=4)
    return return_value
