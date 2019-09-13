import hashlib
import hmac
import json
import sys
import time

from future.moves.urllib.parse import quote_plus

import requests

from aussieaddonscommon import exceptions
from aussieaddonscommon import session
from aussieaddonscommon import utils

import resources.lib.config as config
import resources.lib.parse as parse


try:
    import StorageServer
except ImportError:
    utils.log('script.common.plugin.cache not found!')
    import resources.lib.storageserverdummy as StorageServer

cache = StorageServer.StorageServer(utils.get_addon_id(), 1)
py2 = sys.version_info < (3, 0)


def fetch_url(url, headers=None):
    """Simple function that fetches a URL using requests."""
    with session.Session() as sess:
        if headers:
            sess.headers.update(headers)
        request = sess.get(url)
        data = request.text
    return data


def get_auth(hn, sess):
    """Calculate signature and build auth URL for a program"""
    ts = str(int(time.time()))
    auth_path = config.AUTH_PATH.format(
        params=config.AUTH_PARAMS.format(ts=ts, hn=hn))
    auth_path_bytes = bytes(auth_path) if py2 else bytes(auth_path, 'utf8')
    secret = bytes(config.SECRET) if py2 else bytes(config.SECRET, 'utf8')
    digest = hmac.new(secret, msg=auth_path_bytes,
                      digestmod=hashlib.sha256).hexdigest()
    auth_url = config.API_BASE_URL.format(
        path='{authpath}&sig={digest}'.format(authpath=auth_path,
                                              digest=digest))
    try:
        res = sess.get(auth_url)
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            utils.dialog_message(
                'Accurate system time required for '
                'playback. Please set the correct system '
                'time/date/timezone for your location and try again.')
            raise exceptions.AussieAddonsException(e)
    return res.text


def cookies_to_string(cookiejar):
    cookies = []
    for cookie in cookiejar:
        cookies.append('{0}={1}; path={2}; domain={3};'.format(
            cookie.name, cookie.value, cookie.path, cookie.domain))
    return ' '.join(cookies)


def get_stream_url(hn, path):

    with session.Session() as sess:
        video_url = config.API_BASE_URL.format(path='/v2{0}'.format(path))
        utils.log("Fetching stream URL: {0}".format(video_url))
        video_data = sess.get(video_url).text
        video_json = json.loads(video_data)
        if video_json.get('playable') is False:
            return {'msg': video_json.get('playableMessage'),
                    'availability': video_json.get('availability')}
        sess.headers = {'User-Agent': config.USER_AGENT}
        for playlist in video_json['_embedded']['playlist']:
            if playlist.get('type') not in ['program', 'livestream']:
                continue
            if 'hls' in playlist.get('streams'):
                hls_streams = playlist['streams'].get('hls')
                stream_url_base = hls_streams.get('sd',
                                                  hls_streams.get('sd-low'))
            if stream_url_base:
                captions_url = playlist.get('captions', {}).get('src-vtt')
                break
        akamai_auth = get_auth(hn, sess)
        request = sess.get(stream_url_base, params={'hdnea': akamai_auth})
        cookies = cookies_to_string(request.cookies)
        stream_url = '{0}|User-Agent={1}&Cookie={2}'.format(
            request.url, quote_plus(config.USER_AGENT),
            quote_plus(cookies))

    return {'stream_url': stream_url, 'captions_url': captions_url}


def get_categories():
    """Returns the list of categories"""
    url = config.API_BASE_URL.format(path='/v2/navigation/mobile')
    category_data = fetch_url(url)
    categories = parse.parse_categories(category_data)
    return categories


def validate_category(keyword):
    """Validate category

    Checks if keyword is in a list of categories from the old/LG
    iview API, and updates if required. Maintains compatibility with old
    favourites links
    """
    if keyword in config.OLD_CATEGORIES:
        return config.OLD_CATEGORIES[keyword]
    else:
        return keyword


def get_cached_feed(url):
    feed = cache.cacheFunction(fetch_url, url)
    return feed


def get_programme_from_feed(keyword):
    keyword = validate_category(keyword)
    utils.log('Getting programme from feed ({0})'.format(keyword))
    feed = get_cached_feed(
        config.API_BASE_URL.format(path='/v2{0}'.format(keyword)))
    shows = parse.parse_programme_from_feed(feed)
    return shows


def get_series_from_feed(series_url):
    utils.log('Fetching series from feed')
    feed = get_cached_feed(config.API_BASE_URL.format(path='/v2{0}{1}'.format(
        series_url, '?embed=seriesList,selectedSeries')))
    return parse.parse_programs_from_feed(feed)


def get_livestreams_from_feed():
    utils.log('Fetching livestreams from feed')
    feed = get_cached_feed(
        config.API_BASE_URL.format(path='/v2{0}'.format('/home')))
    return parse.parse_livestreams_from_feed(feed)


def get_search_results(search_string):
    utils.log('Fetching search results')
    feed = fetch_url(config.API_BASE_URL.format(
        path='/v2/search?keyword={0}'.format(search_string)))
    return parse.parse_search_results(feed)
