#
#  ABC iView XBMC Addon
#  Copyright (C) 2012 Andy Botting
#
#  This addon includes code from python-iview
#  Copyright (C) 2009-2012 by Jeremy Visser <jeremy@visser.name>
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
import gzip
import ssl
from StringIO import StringIO

try:
    import StorageServer
except:
    utils.log("script.common.plugin.cache not found!")
    import storageserverdummy as StorageServer

cache = StorageServer.StorageServer(config.ADDON_ID, 1)

class JsonRedirectHandler(urllib2.HTTPRedirectHandler): 
    def http_error_301(self, req, fp, code, msg, headers):
        utils.log('Redirected to: %s' % headers['location'])
        headers['location'] += '.json'
        return urllib2.HTTPRedirectHandler.http_error_301(self, req, fp, code, msg, headers) 

def fetch_url(url, headers={}):
    """ Fetches a URL using urllib2 with some basic retry.
        An exception is raised if an error (e.g. 404) occurs after the max
        number of retries.
    """
    utils.log("Fetching URL: %s" % url)
    request = urllib2.Request(url, None, dict(headers.items() + {
        'User-Agent' : config.user_agent
    }.items()))

    attempts = 10
    attempt = 0
    fail_exception = Exception("Unknown failure in URL fetch")

    # monkey patch SSL context to fix SSL errors on some platforms w/ python >= 2.7.9
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

    # Attempt $attempt times and increase the timeout each time
    while attempt < attempts:
        try:
            timeout = 10 * (attempt + 1)
            http = urllib2.urlopen(request, timeout=timeout)
            return http.read()
        except Exception, e:
            fail_exception = e
            attempt += 1
            utils.log('Error fetching URL: "%s". Attempting to retry URL fetch %d/%d' % (e, attempt, attempts))

    # Pass the last exception though
    raise fail_exception

def fetch_protected_url(url):
    """ For protected URLs we add or Auth header when fetching
    """
    headers = {'Authorization': 'Basic ZmVlZHRlc3Q6YWJjMTIz'}
    return fetch_url(url, headers)

def get_config():
    """This function fetches the iView "config". Among other things,
        it tells us an always-metered "fallback" RTMP server, and points
        us to many of iView's other XML files.
    """
    iview_config = fetch_url(config.config_url)
    return parse.parse_config(iview_config)

def get_auth(iview_config):
    """This function performs an authentication handshake with iView.
        Among other things, it tells us if the connection is unmetered,
        and gives us a one-time token we need to use to speak RTSP with
        ABC's servers, and tells us what the RTMP URL is.
    """
    auth_config = fetch_url(config.auth_url)
    return parse.parse_auth(auth_config, iview_config)

def get_categories(iview_config):
    """Returns the list of categories
    """
    url = config.base_url + iview_config['categories_url']
    category_data = fetch_url(url)
    categories = parse.parse_categories(category_data)
    return categories

def get_feed(keyword):
    utils.log("Fetching feed")
    url = config.feed_url + '?keyword=' + keyword
    feed = cache.cacheFunction(fetch_protected_url, url)
    return feed

def get_programme_from_feed(keyword):
    utils.log("Getting programme from feed (%s)" % keyword)
    feed = get_feed(keyword)
    shows = parse.parse_programme_from_feed(feed)
    return shows

def get_series_from_feed(series, category='0-z'):
    utils.log("Fetching series feed")
    feed = get_feed(category)
    programs = parse.parse_programs_from_feed(feed)
    filtered = []
    for p in programs:
        if p.title == series:
            filtered.append(p)
    return filtered
