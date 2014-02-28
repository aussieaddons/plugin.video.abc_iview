#
#  ABC iView XBMC Plugin
#  Copyright (C) 2012 Andy Botting
#
#  This plugin includes from from python-iview
#  Copyright (C) 2009-2012 by Jeremy Visser <jeremy@visser.name>
#
#  This plugin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This plugin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this plugin. If not, see <http://www.gnu.org/licenses/>.
#

import urllib2
import config
import parse
import utils
import gzip
from StringIO import StringIO

cache = False

def fetch_url(url):
    """Simple function that fetches a URL using urllib2.
        An exception is raised if an error (e.g. 404) occurs.
    """
    utils.log("Fetching URL: %s" % url)
    http = urllib2.urlopen(
        urllib2.Request(url, None, {
            'User-Agent' : config.user_agent,
            'Accept-Encoding' : 'gzip'
        })
    )
    headers = http.info()
    if 'content-encoding' in headers.keys() and headers['content-encoding'] == 'gzip':
        data = StringIO(http.read())
        return gzip.GzipFile(fileobj=data).read()
    else:
        return http.read()


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

def get_programme(iview_config, keyword):
    """This function pulls in the by-keyword index, which contains the TV
        series that are available to us, filtered by the given keyword.
        Using 0-z as the keyword gives the complete list.
        Unlike the seriesIndex list, this gives all the JSON fields.
    """
    url = iview_config['api_url'] + 'keyword=' + keyword
    index_data = fetch_url(url)
    programme = parse.parse_index(index_data)
    return programme


def get_series_items(iview_config, series_id):
    """This function fetches the series detail page for the selected series
        which contain the items (i.e. the actual episodes).
    """
    series_json = fetch_url(iview_config['api_url'] + 'series=%s' % series_id)
    return parse.parse_series_items(series_json)

