from urllib.parse import urlparse, parse_qs
from urllib.request import build_opener
from html.parser import HTMLParser

from typing import Text, Optional, Tuple, Dict

'''
This file is for parsing documents and matching the relevant information.
'''


class WebsiteParser(HTMLParser):
    '''Parser which actually scrapes through the website.'''

    def handle_starttag(self, tag: Text, attrs: Dict[Text, Text]) -> None:
        if tag != 'a':
            return
        for key, value in attrs:
            if key != 'href':
                continue
            match_return = match_handles(value)
            if match_return is not None:
                handle_id, handle_value = match_return
                self.handles[handle_id] = handle_value


    def find_handles(self, url) -> Dict[Text, Text]:
        self.baseUrl = url
        self.handles: Dict[Text, Text] = {}

        # work-around for when sites reject the standard User-Agent generated.
        url_opener = build_opener()
        url_opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        response = url_opener.open(url, timeout=3)
        header = response.getheader('Content-Type')
        if 'text/html' in header:
            read_response = response.read()
            if 'charset=utf-8' in header.lower():
                read_response = read_response.decode('utf-8')
            self.feed(read_response)
            print(self.handles)
            return self.handles


def match_handles(url: Text) -> Optional[Tuple[Text, Text]]:
    parse_response = urlparse(url)

    # splitting on '/' and fetching first section to allow for longer paths
    if 'facebook.com' in parse_response.netloc:
        return 'facebook', parse_response.path.strip('/').split('/')[0]
    if 'twitter.com' in parse_response.netloc:
        return 'twitter', parse_response.path.strip('/').split('/')[0]
    if 'apps.apple.com' in parse_response.netloc or 'itunes.apple.com' in parse_response.netloc:
        path_split = parse_response.path.split('/')
        # Searching for 'id' may be naive, for example if the company name starts with id.
        # It also removes the need to deal with the optional media-type specifier: '?mt=8'
        id_index = path_split.index('app') + 2
        assert path_split[id_index].startswith('id')
        return 'ios', path_split[id_index].strip('id')
    if 'play.google.com' in parse_response.netloc:
        return 'google', parse_qs(parse_response.query)['id'][0]

    return None
