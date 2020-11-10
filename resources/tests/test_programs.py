from __future__ import absolute_import, unicode_literals

import importlib
import io
import os

try:
    import mock
except ImportError:
    import unittest.mock as mock

import responses

import testtools

import resources.lib.config as config
from resources.tests.fakes import fakes


class ProgramsTests(testtools.TestCase):

    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/json/show.json'), 'rb') as f:
            self.SHOW_JSON = io.BytesIO(f.read()).read()

    def setUp(self):
        super(ProgramsTests, self).setUp()
        self.mock_plugin = fakes.FakePlugin()
        self.patcher = mock.patch.dict('sys.modules',
                                       xbmcplugin=self.mock_plugin)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        global programs
        programs = importlib.import_module('resources.lib.programs')

    def tearDown(self):
        super(ProgramsTests, self).tearDown()
        self.patcher.stop()
        self.mock_plugin = None

    @mock.patch('resources.lib.classes.utils.get_kodi_major_version')
    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv', ['plugin://plugin.video.abc_iview/', '5',
                             '?action=series_list&url=%2fshow%2fsesame-street&'
                             'type=Series',
                             'resume:false'])
    @responses.activate
    def test_make_programs_list_titles(self, mock_listitem, mock_version):
        mock_listitem.side_effect = fakes.FakeListItem
        mock_version.return_value = 15
        show_path = '/show/sesame-street'
        show_url = config.API_BASE_URL.format(
            path='/v2{0}{1}'.format(show_path,
                                    '?embed=seriesList,selectedSeries'))
        responses.add(responses.GET, show_url, body=self.SHOW_JSON)

        programs.make_programs_list({'url': '/show/sesame-street'})
        for index, expected in enumerate(fakes.EXPECTED_SHOW_TITLES):
            li = self.mock_plugin.directory[index].get('listitem')
            observed = li.getLabel()
            self.assertEqual(expected, observed)
