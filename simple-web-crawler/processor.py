import logging
import json

from queue import Queue
from threading import Thread
from urllib.error import HTTPError

from matching import WebsiteParser

from typing import Text, List, Dict

'''
This file contains the driving code directing which files to match and aggregating the results.
'''

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def scrape_inputs(inputs) -> Text:
    parser = WebsiteParser()
    results: List[Dict[Text, Text]] = []

    for input in inputs:
        try:
            results.append(parser.find_handles(input))
        except HTTPError as error:
            print(f'failed while parsing input: {input}, {error}')
            if error.code == 503:
                # This is easily mitigated with the Python ``Requests`` external library.
                print('503 errors are likely due to being identified '
                      'as non-human traffic, or gated input was given.')

    return_value = json.dumps(results, indent=4)
    return return_value
