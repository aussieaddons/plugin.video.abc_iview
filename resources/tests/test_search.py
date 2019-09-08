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

from resources.lib import config
from resources.tests.fakes import fakes
import xbmcaddon


class SearchTests(testtools.TestCase):

    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/json/search.json'), 'rb') as f:
            self.SEARCH_JSON = io.BytesIO(f.read()).read()

    def setUp(self):
        super(SearchTests, self).setUp()
        self.mock_plugin = fakes.FakePlugin()
        self.patcher = mock.patch.dict('sys.modules',
                                       xbmcplugin=self.mock_plugin)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        global search
        search = importlib.import_module('resources.lib.search')

    def tearDown(self):
        super(SearchTests, self).tearDown()
        self.patcher.stop()
        self.mock_plugin = None

    def test_get_search_history(self):
        with mock.patch.object(xbmcaddon.Addon, 'getSetting') as mock_setting:
            mock_setting.return_value = fakes.SEARCH_HISTORY_SERIALIZED
            expected = fakes.EXPECTED_SEARCH_HISTORY[:]
            observed = search.get_search_history()
            self.assertEqual(expected, observed)

    @mock.patch.object(xbmcaddon.Addon, 'setSetting')
    def test_set_search_history(self, mock_setting):
        search.set_search_history(fakes.EXPECTED_SEARCH_HISTORY[:])
        mock_setting.assert_called_with('SEARCH_HISTORY',
                                        fakes.SEARCH_HISTORY_SERIALIZED)

    def test_add_to_search_history(self):
        with mock.patch('resources.lib.search.get_search_history',
                        return_value=fakes.EXPECTED_SEARCH_HISTORY[:]):
            with mock.patch('resources.lib.search.set_search_history') \
                    as mock_set_search_history:
                expected_history = fakes.EXPECTED_SEARCH_HISTORY[:]
                expected_history.append('abcd')
                search.add_to_search_history('abcd')
                mock_set_search_history.assert_called_with(expected_history)

    def test_remove_from_search_history(self):
        with mock.patch('resources.lib.search.get_search_history',
                        return_value=fakes.EXPECTED_SEARCH_HISTORY[:]):
            with mock.patch('resources.lib.search.set_search_history') \
                    as mock_set_search_history:
                expected_history = fakes.EXPECTED_SEARCH_HISTORY[:]
                expected_history.remove('foo')
                search.remove_from_search_history('foo')
                mock_set_search_history.assert_called_with(expected_history)

    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.abc_iview/', '5',
                 '?action=category_list&category=search',
                 'resume:false'])
    def test_make_search_history_list(self, mock_listitem):
        mock_listitem.side_effect = fakes.FakeListItem
        with mock.patch('resources.lib.search.get_search_history',
                        return_value=fakes.EXPECTED_SEARCH_HISTORY[:]):
            expected_titles = ['New Search']
            expected_titles.extend(fakes.EXPECTED_SEARCH_HISTORY)
            search.make_search_history_list()
            for index, expected in enumerate(expected_titles):
                url = self.mock_plugin.directory[index].get('url')
                url_query = dict(parse_qsl(urlparse(url)[4]))
                observed = url_query.get('name')
                self.assertEqual(expected, observed)

    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv',
                ['plugin://plugin.video.abc_iview/', '5',
                 '?action=searchhistory&name=news',
                 'resume:false'])
    @responses.activate
    def test_make_search_list(self, mock_listitem):
        mock_listitem.side_effect = fakes.FakeListItem
        search_path = '/search?keyword=news'
        search_url = config.API_BASE_URL.format(
            path='/v2{0}'.format(search_path))
        responses.add(responses.GET, search_url, body=self.SEARCH_JSON)
        search.make_search_list({'name': 'news'})
        for index, expected in enumerate(fakes.EXPECTED_SEARCH_TITLES):
            url = self.mock_plugin.directory[index].get('url')
            url_query = dict(parse_qsl(urlparse(url)[4]))
            observed = url_query.get('title')
            self.assertEqual(expected, observed)
