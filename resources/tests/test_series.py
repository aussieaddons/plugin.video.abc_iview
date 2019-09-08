from __future__ import absolute_import, unicode_literals

import importlib
import io
import os

try:
    import mock
except ImportError:
    import unittest.mock as mock

from future.moves.urllib.parse import parse_qsl, urlparse

import responses

import testtools

import resources.lib.config as config
from resources.tests.fakes import fakes


class SeriesTests(testtools.TestCase):

    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/json/channel.json'), 'rb') as f:
            self.CHANNEL_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/collection.json'), 'rb') as f:
            self.COLLECTION_JSON = io.BytesIO(f.read()).read()

    def setUp(self):
        super(SeriesTests, self).setUp()
        self.mock_plugin = fakes.FakePlugin()
        self.patcher = mock.patch.dict('sys.modules',
                                       xbmcplugin=self.mock_plugin)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        global series
        series = importlib.import_module('resources.lib.series')

    def tearDown(self):
        super(SeriesTests, self).tearDown()
        self.patcher.stop()
        self.mock_plugin = None

    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv', ['plugin://plugin.video.abc_iview/', '5',
                             '?category=%2fchannel%2fabc4kids',
                             'resume:false'])
    @responses.activate
    def test_make_series_list_titles(self, mock_listitem):
        mock_listitem.side_effect = fakes.FakeListItem

        channel_path = '/channel/abc4kids'
        channel_url = config.API_BASE_URL.format(
            path='/v2{0}'.format(channel_path))
        collection_path = '/collection/1962'
        collection_url = config.API_BASE_URL.format(
            path='/v2{0}'.format(collection_path))
        responses.add(responses.GET, channel_url, body=self.CHANNEL_JSON)
        responses.add(responses.GET, collection_url, body=self.COLLECTION_JSON)

        series.make_series_list({'category': channel_path})
        for index, expected in enumerate(fakes.EXPECTED_SERIES_TITLES):
            url = self.mock_plugin.directory[index].get('url')
            url_query = dict(parse_qsl(urlparse(url)[4]))
            observed = url_query.get('title')
            self.assertEqual(expected, observed)

    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv', ['plugin://plugin.video.abc_iview/', '5',
                             '?category=%2fchannel%2fabc4kids',
                             'resume:false'])
    @responses.activate
    def test_make_series_list_episode_count(self, mock_listitem):
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

        series.make_series_list({'category': channel_path})
        for index, expected in enumerate(fakes.EXPECTED_EPISODE_COUNTS):
            url = self.mock_plugin.directory[index].get('url')
            url_query = dict(parse_qsl(urlparse(url)[4]))
            observed_str = url_query.get('num_episodes')
            if observed_str:
                observed = int(observed_str)
            else:
                observed = observed_str
            self.assertEqual(expected, observed)