from __future__ import absolute_import, unicode_literals

import io
import json
import os

try:
    import mock
except ImportError:
    import unittest.mock as mock

from future.moves.urllib.parse import quote_plus

import requests

import responses

import testtools

import resources.lib.comm as comm
import resources.lib.config as config
from resources.tests.fakes import fakes


class CommTests(testtools.TestCase):

    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/text/sign'), 'rb') as f:
            self.AUTH_RESP_TEXT = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/navigation.json'), 'rb') as f:
            self.NAV_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/channel.json'), 'rb') as f:
            self.CHANNEL_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/collection.json'), 'rb') as f:
            self.COLLECTION_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/show.json'), 'rb') as f:
            self.SHOW_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_ss.json'), 'rb') as f:
            self.VIDEO_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_tb.json'), 'rb') as f:
            self.VIDEO_JSON_NA = io.BytesIO(f.read()).read()


    @responses.activate
    def test_fetch_url_headers(self):
        responses.add(responses.GET, 'https://foo.bar/', body='foo',
                      status=200)
        s = requests.Session()
        with mock.patch('resources.lib.comm.session.Session', return_value=s):
            comm.fetch_url('https://foo.bar', headers={'foo': 'bar'})
            self.assertIn('foo', s.headers)

    @responses.activate
    def test_fetch_url(self):
        responses.add(responses.GET, 'https://foo.bar/', body='foo',
                      status=200)
        observed = comm.fetch_url('https://foo.bar')
        expected = 'foo'
        self.assertEqual(expected, observed)

    @responses.activate
    @mock.patch('time.time')
    def test_get_auth(self, mock_time):
        responses.add(responses.GET, fakes.EXPECTED_AUTH_URL,
                      body=self.AUTH_RESP_TEXT,
                      status=200)
        mock_time.return_value = 1565669764
        observed = comm.get_auth('ZW1939A016S00', comm.session.Session())
        expected = self.AUTH_RESP_TEXT
        self.assertEqual(expected, observed)

    def test_cookies_to_string(self):
        cj = fakes.COOKIEJAR
        observed = comm.cookies_to_string(cj)
        expected = 'Foo=Bar; path=Somewhere; domain=foo.org;'
        self.assertEqual(expected, observed)

    @mock.patch('resources.lib.comm.get_auth')
    @responses.activate
    def test_get_stream_url(self, mock_auth):
        path = '/video/ZW1939A025S00'
        video_url = config.API_BASE_URL.format(path='/v2{0}'.format(path))

        req = requests.Request('GET', fakes.EXPECTED_HLS_URL,
                               params={'hdnea': self.AUTH_RESP_TEXT})
        prepared = req.prepare()
        url = prepared.url

        responses.add(responses.GET, video_url, body=self.VIDEO_JSON)
        responses.add(responses.GET, url, body='#EXTM3U',
                      headers={'Set-Cookie': fakes.AUTH_COOKIE}, status=200)
        mock_auth.return_value = self.AUTH_RESP_TEXT
        observed = comm.get_stream_url(fakes.HN, path)

        expected = {'stream_url': fakes.RESOLVED_URL.format(
            quote_plus(self.AUTH_RESP_TEXT, safe='~'),
            quote_plus(config.USER_AGENT)),
                    'captions_url': fakes.EXPECTED_SUB_URL}
        # responses doesn't handle cookie domain/paths correctly atm, so
        # the expected stream_url omits the domain value.
        self.assertEqual(expected, observed)

    @responses.activate
    def test_get_categories(self):
        responses.add(responses.GET,
                      config.API_BASE_URL.format(path='/v2/navigation/mobile'),
                      body=self.NAV_JSON)
        category_list = comm.get_categories()
        expected_len = 17
        observed_len = len(category_list)
        self.assertEqual(expected_len, observed_len)

    def test_validate_category(self):
        for cat in config.OLD_CATEGORIES.keys():
            observed = comm.validate_category(cat)
            self.assertTrue(observed.startswith(('channel', 'category')))

    @responses.activate
    def test_get_programme_from_feed(self):
        channel_path = '/channel/abc4kids'
        channel_url = config.API_BASE_URL.format(
            path='/v2{0}'.format(channel_path))
        collection_path = '/collection/1962'
        collection_url = config.API_BASE_URL.format(
            path='/v2{0}'.format(collection_path))
        responses.add(responses.GET, channel_url, body=self.CHANNEL_JSON)
        responses.add(responses.GET, collection_url, body=self.COLLECTION_JSON)
        observed = comm.get_programme_from_feed(channel_path)
        import json
        self.assertEqual([x.get('title') for x in
                          json.loads(self.COLLECTION_JSON).get('items')],
                         [x.title for x in observed])

    @responses.activate
    def test_get_series_from_feed(self):
        show_path = '/show/sesame-street'
        show_url = config.API_BASE_URL.format(
            path='/v2{0}{1}'.format(
                show_path, '?embed=seriesList,selectedSeries'))
        responses.add(responses.GET, show_url, body=self.SHOW_JSON)
        observed = comm.get_series_from_feed(show_path)
        json_data = json.loads(self.SHOW_JSON)['_embedded']['selectedSeries'][
            '_embedded'].get('videoEpisodes')
        expected_episode_titles = [x.get('title') for x in json_data]
        observed_episode_titles = [x.episode_title for x in observed]
        self.assertEqual(expected_episode_titles, observed_episode_titles)

