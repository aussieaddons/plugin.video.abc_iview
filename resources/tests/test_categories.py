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


class CategoriesTests(testtools.TestCase):

    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/json/navigation.json'), 'rb') as f:
            self.NAV_JSON = io.BytesIO(f.read()).read()

    def setUp(self):
        super(CategoriesTests, self).setUp()
        self.mock_plugin = fakes.FakePlugin()
        self.patcher = mock.patch.dict('sys.modules',
                                       xbmcplugin=self.mock_plugin)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        global categories
        categories = importlib.import_module('resources.lib.categories')

    def tearDown(self):
        super(CategoriesTests, self).tearDown()
        self.patcher.stop()
        self.mock_plugin = None

    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv', ['plugin://plugin.video.abc_iview/', '5',
                             '',
                             'resume:false'])
    @responses.activate
    def test_categories_names(self, mock_listitem):
        mock_listitem.side_effect = fakes.FakeListItem
        responses.add(responses.GET,
                      config.API_BASE_URL.format('/v2/navigation/mobile'),
                      body=self.NAV_JSON)
        categories.make_category_list()
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
                      config.API_BASE_URL.format('/v2/navigation/mobile'),
                      body=self.NAV_JSON)
        categories.make_category_list()
        for index, expected in enumerate(fakes.EXPECTED_CATEGORY_PATHS):
            url = self.mock_plugin.directory[index].get('url')
            url_query = dict(parse_qsl(urlparse(url)[4]))
            observed = url_query.get('category')
            self.assertEqual(expected, observed)
