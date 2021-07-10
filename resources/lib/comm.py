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

import resources.lib.classes as classes
import resources.lib.config as config
import resources.lib.parse as parse

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
        if e.response.status_code in [401, 404]:
            utils.dialog_message(
                'Accurate system time required for '
                'playback. Please set the correct system '
                'time/date/timezone for your location and try again.')
            raise exceptions.AussieAddonsException(e)
        else:
            raise
    return res.text


def cookies_to_string(cookiejar):
    cookies = []
    for cookie in cookiejar:
        cookies.append('{0}={1}; path={2}; domain={3};'.format(
            cookie.name, cookie.value, cookie.path, cookie.domain))
    return ' '.join(cookies)


def get_stream_program(params):
    with session.Session() as sess:
        video_url = config.API_BASE_URL.format(
            path='/v2{0}'.format(params.get('url')))
        utils.log("Fetching stream URL: {0}".format(video_url))
        try:
            video_data = sess.get(video_url).text
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                error_data = json.loads(e.response.text)
                msg = error_data.get('message')
                p = classes.Program()
                p.failure_msg = {
                    'msg': msg,
                    'availability': 'The content may have expired, '
                                    'please refresh the listing and try again'}
                return p
        video_json = json.loads(video_data)
        if video_json.get('playable') is False:
            p = classes.Program()
            p.failure_msg = {'msg': video_json.get('playableMessage'),
                             'availability': video_json.get('availability')}
            return p
        sess.headers = {'User-Agent': config.USER_AGENT}
        captions_url = None
        for playlist in video_json['_embedded']['playlist']:
            if playlist.get('type') not in ['program', 'livestream']:
                continue
            if 'hls' in playlist.get('streams'):
                hls_streams = playlist['streams'].get('hls')
                stream_url_base = hls_streams.get(
                    '720', hls_streams.get('sd', hls_streams.get('sd-low')))
            if stream_url_base:
                captions_url = playlist.get('captions', {}).get('src-vtt')
                break
        akamai_auth = get_auth(params.get('house_number'), sess)
        request = sess.get(stream_url_base, params={'hdnea': akamai_auth})
        cookies = cookies_to_string(request.cookies)
        stream_url = '{0}|User-Agent={1}&Cookie={2}'.format(
            request.url, quote_plus(config.USER_AGENT),
            quote_plus(cookies))
        p = parse.parse_stream_from_json(video_json)
        p.stream_url = stream_url
        p.captions_url = captions_url
    return p


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


def get_collections_from_feed(params):
    utils.log(
        'Getting collections from feed ({0})'.format(params.get('category')))
    feed = fetch_url(config.API_BASE_URL.format(
        path='/v2{0}'.format(params.get('category'))))
    collects = parse.parse_collections_from_feed(feed, params)
    return collects


def get_collection_from_feed(params):
    keyword = params.get('collection_id')
    utils.log('Getting collection from feed ({0})'.format(params.get('title')))
    feed = fetch_url(
        config.API_BASE_URL.format(path='/v2/collection/{0}'.format(keyword)))
    collection = parse.parse_programme_from_feed(feed, params)
    return collection


def get_atoz_programme_from_feed(params):
    params['category'] = validate_category(params['category'])
    collects = get_collections_from_feed(params)
    atoz_list = [x for x in collects if 'a-z' in x.get_title().lower()]
    if len(atoz_list) > 0:
        atoz_id = atoz_list[0].collection_id
        feed = fetch_url(config.API_BASE_URL.format(
            path='/v2/collection/{0}'.format(atoz_id)))
        shows = parse.parse_programme_from_feed(feed, params)
        return shows
    else:
        return atoz_list


def get_series_from_feed(series_url, from_series_list=False):
    utils.log('Fetching series from feed')
    query = '?embed=seriesList,selectedSeries'
    feed = fetch_url(config.API_BASE_URL.format(path='/v2{0}{1}'.format(
        series_url, query)))
    return parse.parse_programs_from_feed(feed, from_series_list)


def get_livestreams_from_feed():
    utils.log('Fetching livestreams from feed')
    feed = fetch_url(
        config.API_BASE_URL.format(path='/v2{0}'.format('/home')))
    return parse.parse_livestreams_from_feed(feed)


def get_search_results(search_string):
    utils.log('Fetching search results')
    feed = fetch_url(config.API_BASE_URL.format(
        path='/v2/search?keyword={0}'.format(search_string)))
    return parse.parse_search_results(feed)
