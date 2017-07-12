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

import requests
import config
import parse
import utils
import json
import threading
import time
import hmac
import hashlib
import urllib
from classes import iviewException
from requests.adapters import HTTPAdapter
# Ignore InsecureRequestWarning warnings
requests.packages.urllib3.disable_warnings()

try:
    import StorageServer
except:
    utils.log('script.common.plugin.cache not found!')
    import storageserverdummy as StorageServer

cache = StorageServer.StorageServer(config.ADDON_ID, 1)


def fetch_url(url, headers=None):
    """
    Simple function that fetches a URL using requests.
    An exception is raised if an error (e.g. 404) occurs.
    """
    utils.log("Fetching URL: %s" % url)
    with requests.Session() as session:
        session.mount('http://', HTTPAdapter(max_retries=5))
        session.mount('https://', HTTPAdapter(max_retries=5))
        session.verify = False

        if headers:
            session.headers.update(headers)

        request = session.get(url)

        try:
            request.raise_for_status()
        except Exception as e:
            # Just re-raise for now
            raise e
        data = request.text
    return data


def fetch_protected_url(url):
    """ For protected URLs we add or Auth header when fetching
    """
    headers = {'Authorization': 'Basic ZmVlZHRlc3Q6YWJjMTIz'}
    return fetch_url(url, headers)


def get_auth(hn):
    """ Calculate signature and build auth URL for a program"""
    ts = str(int(time.time()))
    path = config.AUTH_URL + 'ts={0}&hn={1}&d=android-mobile'.format(ts, hn)
    digest = hmac.new(config.SECRET, msg=path,
                      digestmod=hashlib.sha256).hexdigest()
    auth_url = config.BASE_URL + path + '&sig=' + digest
    try:
        res = requests.get(auth_url, verify=False)
        res.raise_for_status()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            utils.dialog_message(
                'Accurate system time required for '
                'playback. Please set the correct system '
                'time/date/timezone for your location and try again.')
            raise iviewException(e)
    return res.text


def cookies_to_string(cookiejar):
    cookies = []
    for cookie in cookiejar:
        cookies.append('{0}={1}; path={2}; domain={3};'.format(
            cookie.name, cookie.value, cookie.path, cookie.domain))
    return ' '.join(cookies)


def get_stream_url(hn, url):
    utils.log("Fetching stream URL: {0}".format(url))
    with requests.Session() as session:
        session.mount('http://', HTTPAdapter(max_retries=5))
        session.mount('https://', HTTPAdapter(max_retries=5))
        session.verify = False
        session.headers = {'User-Agent': config.USER_AGENT}

        akamai_auth = get_auth(hn)
        akamai_url = "{0}?hdnea={1}".format(url, akamai_auth)

        request = session.get(akamai_url)
        request.raise_for_status()
        cookies = cookies_to_string(request.cookies)
        stream_url = '{0}|User-Agent={1}&Cookie={2}'.format(
            akamai_url, urllib.quote(config.USER_AGENT), urllib.quote(cookies))

    return stream_url


def get_categories():
    """Returns the list of categories
    """
    url = config.CONFIG_URL
    category_data = fetch_url(url)
    categories = parse.parse_categories(category_data)
    return categories


def validate_category(keyword):
    """
    Checks if keyword is in a list of categories from the old/LG
    iview API, and updates if required. Maintains compatibility with old
    favourites links
    """
    if keyword in config.CATEGORIES:
        return config.CATEGORIES[keyword]
    else:
        return keyword


def get_feed(keyword):
    url = config.FEED_URL.format(keyword)
    feed = cache.cacheFunction(fetch_url, url)
    return feed


def get_programme_from_feed(keyword):
    utils.log('Getting programme from feed (%s)' % keyword)
    feed = get_feed(keyword)
    shows = parse.parse_programme_from_feed(feed, keyword)
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
