from __future__ import absolute_import, unicode_literals

import importlib
import io
import os

try:
    import mock
except ImportError:
    import unittest.mock as mock

from future.moves.urllib.parse import parse_qsl, quote_plus, urlparse

import requests

import responses

import testtools
import resources.lib.config as config
from resources.tests.fakes import fakes


class DefaultTests(testtools.TestCase):

    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/json/channel.json'), 'rb') as f:
            self.CHANNEL_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/collection.json'), 'rb') as f:
            self.COLLECTION_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/live.json'), 'rb') as f:
            self.LIVE_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/navigation.json'), 'rb') as f:
            self.NAV_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/search.json'), 'rb') as f:
            self.SEARCH_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/show.json'), 'rb') as f:
            self.SHOW_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_ss.json'), 'rb') as f:
            self.VIDEO_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/live_video.json'), 'rb') as f:
            self.LIVE_VIDEO_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/text/sign'), 'rb') as f:
            self.AUTH_RESP_TEXT = io.BytesIO(f.read()).read()

    def setUp(self):
        super(DefaultTests, self).setUp()
        self.mock_plugin = fakes.FakePlugin()
        self.patcher = mock.patch.dict('sys.modules',
                                       xbmcplugin=self.mock_plugin)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        for module in ['categories', 'search', 'series', 'programs', 'play']:
            setattr(self, module,
                    importlib.import_module(
                        'resources.lib.{0}'.format(module)))
            self.assertEqual(self.mock_plugin,
                             getattr(self, module).xbmcplugin)
        global default
        default = importlib.import_module('default')

    def tearDown(self):
        super(DefaultTests, self).tearDown()
        self.patcher.stop()
        self.mock_plugin = None

    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.abc_iview/', '5',
                 '?action=category_list&category=%2fchannel%2fabc4kids',
                 'resume:false'])
    @responses.activate
    def test_default_series(self, mock_listitem):
        mock_listitem.side_effect = fakes.FakeListItem
        channel_path = '/channel/abc4kids'
        channel_url = config.API_BASE_URL.format(
            path='/v2{0}'.format(channel_path))
        collection_path = '/collection/1962'
        collection_url = config.API_BASE_URL.format(
            path='/v2{0}'.format(collection_path))
        responses.add(responses.GET, channel_url, body=self.CHANNEL_JSON)
        responses.add(responses.GET, collection_url,
                      body=self.COLLECTION_JSON)

        default.main()
        for index, expected in enumerate(fakes.EXPECTED_SERIES_TITLES):
            url = self.mock_plugin.directory[index].get('url')
            url_query = dict(parse_qsl(urlparse(url)[4]))
            observed = url_query.get('title')
            self.assertEqual(expected, observed)

    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv', ['plugin://plugin.video.abc_iview/', '5',
                             '',
                             'resume:false'])
    @responses.activate
    def test_default_categories_names(self, mock_listitem):
        mock_listitem.side_effect = fakes.FakeListItem
        responses.add(responses.GET,
                      config.API_BASE_URL.format(path='/v2/navigation/mobile'),
                      body=self.NAV_JSON)
        default.main()
        for index, expected in enumerate(fakes.EXPECTED_CATEGORY_TITLES):
            observed = self.mock_plugin.directory[index].get(
                'listitem').getLabel()
            self.assertEqual(expected, observed)

    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv', ['plugin://plugin.video.abc_iview/', '5',
                             '',
                             'resume:false'])
    @responses.activate
    def test_default_categories_paths(self, mock_listitem):
        mock_listitem.side_effect = fakes.FakeListItem
        responses.add(responses.GET,
                      config.API_BASE_URL.format(path='/v2/navigation/mobile'),
                      body=self.NAV_JSON)
        default.main()
        for index, expected in enumerate(fakes.EXPECTED_CATEGORY_PATHS):
            url = self.mock_plugin.directory[index].get('url')
            url_query = dict(parse_qsl(urlparse(url)[4]))
            observed = url_query.get('category')
            self.assertEqual(expected, observed)

    @mock.patch('resources.lib.classes.utils.get_kodi_major_version')
    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv', ['plugin://plugin.video.abc_iview/', '5',
                             ('?action=series_list&url=%2fshow%2fsesame-street'
                              '&type=Series'),
                             'resume:false'])
    @responses.activate
    def test_default_programs_episode_titles(self, mock_listitem,
                                             mock_version):
        mock_listitem.side_effect = fakes.FakeListItem
        mock_version.return_value = 15
        show_path = '/show/sesame-street'
        show_url = config.API_BASE_URL.format(
            path='/v2{0}{1}'.format(show_path,
                                    '?embed=seriesList,selectedSeries'))
        responses.add(responses.GET, show_url, body=self.SHOW_JSON)
        default.main()
        for index, expected in enumerate(fakes.EXPECTED_SHOW_TITLES):
            url = self.mock_plugin.directory[index].get('url')
            url_query = dict(parse_qsl(urlparse(url)[4]))
            observed = url_query.get('episode_title')
            self.assertEqual(expected, observed)

    @mock.patch('time.time')
    @mock.patch('resources.lib.classes.utils.get_kodi_major_version')
    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv', ['plugin://plugin.video.abc_iview/', '5',
                             ('?action=program_list&url=%2fvideo%2fZW1939A025S'
                              '00&type=Program&house_number=ZW1939A025S00'),
                             'resume:false'])
    @responses.activate
    def test_default_play(self, mock_listitem, mock_version, mock_time):
        mock_listitem.side_effect = fakes.FakeListItem
        mock_version.return_value = 15
        mock_time.return_value = 1565672000
        path = '/video/ZW1939A025S00'
        video_url = config.API_BASE_URL.format(path='/v2{0}'.format(path))

        req = requests.Request('GET', fakes.EXPECTED_HLS_URL,
                               params={'hdnea': self.AUTH_RESP_TEXT})
        prepared = req.prepare()
        url = prepared.url

        responses.add(responses.GET, video_url, body=self.VIDEO_JSON)
        responses.add(responses.GET, url, body='#EXTM3U',

                      headers={'Set-Cookie': fakes.AUTH_COOKIE}, status=200)
        responses.add(responses.GET, fakes.AUTH_URL_DEFAULT_TEST,
                      body=self.AUTH_RESP_TEXT, status=200)
        default.main()
        observed = self.mock_plugin.resolved[2].getPath()
        expected = fakes.RESOLVED_URL.format(
            quote_plus(self.AUTH_RESP_TEXT, safe='~'),
            quote_plus(config.USER_AGENT))
        self.assertEqual(expected, observed)

    @mock.patch('time.time')
    @mock.patch('resources.lib.classes.utils.get_kodi_major_version')
    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv', ['plugin://plugin.video.abc_iview/', '5',
                             ('?action=series_list&description=We%27re%20Going'
                              '%20On%20A%20Bear%20Hunt&duration=1465&house_num'
                              'ber=ZW0659A001S00&rating=PG&thumb=https%3a%2f%2'
                              'fcdn.iview.abc.net.au%2fthumbs%2fi%2fzw%2fZW065'
                              '9A001S00_58afb2558244b.jpg&title=We%27re%20Goin'
                              'g%20On%20A%20Bear%20Hunt&type=Program&url=%2fvi'
                              'deo%2fZW0659A001S00'),
                             'resume:false'])
    @responses.activate
    def test_default_play_feature(self, mock_listitem, mock_version,
                                  mock_time):
        mock_listitem.side_effect = fakes.FakeListItem
        mock_version.return_value = 15
        mock_time.return_value = 1565672000

        path = '/video/ZW0659A001S00'
        video_url = config.API_BASE_URL.format(path='/v2{0}'.format(path))
        req = requests.Request('GET', fakes.EXPECTED_HLS_URL,
                               params={'hdnea': self.AUTH_RESP_TEXT})
        prepared = req.prepare()
        url = prepared.url
        responses.add(responses.GET, video_url, body=self.VIDEO_JSON)
        responses.add(responses.GET, url, body='#EXTM3U',
                      headers={'Set-Cookie': fakes.AUTH_COOKIE},
                      status=200)
        responses.add(responses.GET, fakes.AUTH_URL_DEFAULT_FEATURE_TEST,
                      body=self.AUTH_RESP_TEXT, status=200)
        default.main()
        observed = self.mock_plugin.resolved[2].getPath()
        expected = fakes.RESOLVED_URL.format(
            quote_plus(self.AUTH_RESP_TEXT, safe='~'),
            quote_plus(config.USER_AGENT))
        self.assertEqual(expected, observed)

    @mock.patch('time.time')
    @mock.patch('resources.lib.classes.utils.get_kodi_major_version')
    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv', ['plugin://plugin.video.abc_iview/', '5',
                             ('?action=livestreams&&fanart=https%3A%2F%2Fcdn.i'
                              'view.abc.net.au%2Fthumbs%2Fi%2Fhttps%3A%2F%2Fcd'
                              'n.iview.abc.net.au%2Fthumbs%2Fi%2Fns%2FNS1413V0'
                              '01S00_5d675fc5f33f1_1020.jpg&house_number=NS141'
                              '3V001S00&thumb=https%3A%2F%2Fcdn.iview.abc.net.'
                              'au%2Fthumbs%2Fi%2Fns%2FNS1413V001S00_5d675fc5f3'
                              '3f1_1020.jpg&title=ABC+NEWS+Live+Stream&type=Pr'
                              'ogram&url=%2Fvideo%2FNS1413V001S00'),
                             'resume:false'])
    @responses.activate
    def test_default_play_livestream(self, mock_listitem, mock_version,
                                     mock_time):
        mock_listitem.side_effect = fakes.FakeListItem
        mock_version.return_value = 15
        mock_time.return_value = 1565672000
        path = '/video/NS1413V001S00'
        video_url = config.API_BASE_URL.format(path='/v2{0}'.format(path))
        req = requests.Request('GET', fakes.EXPECTED_LIVE_HLS_URL,
                               params={'hdnea': self.AUTH_RESP_TEXT})
        prepared = req.prepare()
        url = prepared.url
        responses.add(responses.GET, video_url, body=self.LIVE_VIDEO_JSON)
        responses.add(responses.GET, url, body='#EXTM3U',
                      headers={'Set-Cookie': fakes.AUTH_COOKIE},
                      status=200)
        responses.add(responses.GET, fakes.AUTH_URL_DEFAULT_LIVE_TEST,
                      body=self.AUTH_RESP_TEXT, status=200)
        default.main()
        observed = self.mock_plugin.resolved[2].getPath()
        expected = fakes.RESOLVED_LIVE_URL.format(
            quote_plus(self.AUTH_RESP_TEXT, safe='~'),
            quote_plus(config.USER_AGENT))
        self.assertEqual(expected, observed)

    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.abc_iview/', '5',
                 '?action=searchhistory&name=news',
                 'resume:false'])
    @responses.activate
    def test_default_search(self, mock_listitem):
        mock_listitem.side_effect = fakes.FakeListItem

        search_path = '/search?keyword=news'
        search_url = config.API_BASE_URL.format(
            path='/v2{0}'.format(search_path))
        responses.add(responses.GET, search_url, body=self.SEARCH_JSON)
        default.main()
        for index, expected in enumerate(fakes.EXPECTED_SEARCH_TITLES):
            url = self.mock_plugin.directory[index].get('url')
            url_query = dict(parse_qsl(urlparse(url)[4]))
            observed = url_query.get('title')
            self.assertEqual(expected, observed)
