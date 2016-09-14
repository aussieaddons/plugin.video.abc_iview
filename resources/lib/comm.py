#
#  ABC iView XBMC Addon
#  Copyright (C) 2012 Andy Botting
#
#  This addon is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This addon is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this addon. If not, see <http://www.gnu.org/licenses/>.
#

import urllib2
import config
import parse
import utils
import ssl
import json
import threading
import cookielib

try:
    import StorageServer
except:
    utils.log('script.common.plugin.cache not found!')
    import storageserverdummy as StorageServer

cache = StorageServer.StorageServer(config.ADDON_ID, 1)
cj = cookielib.CookieJar()
handler = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(handler)
opener.addheaders = config.user_agent


def fetch_url(url, headers={}):
    """ Fetches a URL using urllib2 with some basic retry.
        An exception is raised if an error (e.g. 404) occurs after the max
        number of retries.
    """
    utils.log('Fetching URL: %s' % url)
    request = urllib2.Request(url, None, dict(headers.items() + {
        'User-Agent': config.USER_AGENT
    }.items()))

    attempts = 10
    attempt = 0
    fail_exception = Exception('Unknown failure in URL fetch')

    # monkey patch SSL context to fix SSL errors on python >= 2.7.9
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

    # Attempt $attempt times and increase the timeout each time
    while attempt < attempts:
        try:
            timeout = 10 * (attempt + 1)
            http = urllib2.urlopen(request, timeout=timeout)
            return http.read()
        except Exception as e:
            fail_exception = e
            attempt += 1
            utils.log('Error fetching URL: "%s". Attempting to retry '
                      'URL fetch %d/%d' % (e, attempt, attempts))

    # Pass the last exception though
    raise fail_exception


def fetch_protected_url(url):
    """ For protected URLs we add or Auth header when fetching
    """
    headers = {'Authorization': 'Basic ZmVlZHRlc3Q6YWJjMTIz'}
    return fetch_url(url, headers)


def fetch_url_withcookies(url, data=None):
    """ Fetches a URL using a cookiejar opener"""
    http = opener.open(url, data=None)
    return http.read()


def get_categories():
    """Returns the list of categories
    """
    url = config.CONFIG_URL
    category_data = fetch_url(url)
    categories = parse.parse_categories(category_data)
    return categories


def get_feed(keyword):
    url = config.FEED_URL.format(keyword)
    feed = cache.cacheFunction(fetch_url, url)
    return feed


def get_programme_from_feed(keyword):
    utils.log('Getting programme from feed (%s)' % keyword)
    feed = get_feed(keyword)
    shows = parse.parse_programme_from_feed(feed)
    return shows


def get_series_from_feed(series_url, ep_count):
    utils.log('Fetching series from feed')
    feed = get_feed(series_url)
    return parse.parse_programs_from_feed(feed, ep_count)


def fetch_related(url, listobj, index):
    related_url = config.FEED_URL.format(url)
    related_data = fetch_url(related_url)
    listobj[index+1] = json.loads(related_data)


def fetch_related_list(urls, listobj):
    utils.log('Downloading episode listings (%d) ...' % len(urls))
    threads = []
    listobj.extend([None for x in range(len(urls))])
    for index, url in enumerate(urls):
        thread = threading.Thread(target=fetch_related,
                                  args=(url, listobj, index))
        thread.daemon = True
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()
