from __future__ import absolute_import, unicode_literals

import importlib
import io
import os
import sys

try:
    import mock
except ImportError:
    import unittest.mock as mock

from future.moves.urllib.parse import quote_plus

import responses

import testtools

import resources.lib.config as config
from resources.tests.fakes import fakes


class PlayTests(testtools.TestCase):

    @classmethod
    def setUpClass(self):
        cwd = os.path.join(os.getcwd(), 'resources/tests')
        with open(os.path.join(cwd, 'fakes/text/sign'), 'rb') as f:
            self.AUTH_RESP_TEXT = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/text/webvtt'), 'rb') as f:
            self.VTT_TEXT = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/navigation.json'), 'rb') as f:
            self.NAV_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_ss.json'), 'rb') as f:
            self.VIDEO_JSON = io.BytesIO(f.read()).read()

    def setUp(self):
        super(PlayTests, self).setUp()
        self.mock_plugin = fakes.FakePlugin()
        self.patcher = mock.patch.dict('sys.modules',
                                       xbmcplugin=self.mock_plugin)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        global play
        play = importlib.import_module('resources.lib.play')

    def tearDown(self):
        super(PlayTests, self).tearDown()
        self.patcher.stop()
        self.mock_plugin = None

    @mock.patch('time.time')
    @mock.patch('resources.lib.classes.utils.get_kodi_major_version')
    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv', ['plugin://plugin.video.abc_iview/', '5',
                             ('?action=program_list&url=%2fvideo%2fZW1939A025S'
                              '00&type=Program&house_number=ZW1939A025S00'
                              '&title=Foobar'),
                             'resume:false'])
    @responses.activate
    def test_play_resolved(self, mock_listitem, mock_version, mock_time):
        mock_listitem.side_effect = fakes.FakeListItem
        mock_version.return_value = 15
        mock_time.return_value = 1565672000
        path = '/video/ZW1939A025S00'
        video_url = config.API_BASE_URL.format(path='/v2{0}'.format(path))
        url = '{0}&hdnea={1}'.format(fakes.EXPECTED_HLS_URL,
                                     self.AUTH_RESP_TEXT.decode('utf-8'))
        video_json_modified = self.VIDEO_JSON.replace(b'"captions": true',
                                                      b'"captions": false')
        responses.add(responses.GET, video_url, body=video_json_modified)
        responses.add(responses.GET, url, body='#EXTM3U',
                      headers={'Set-Cookie': fakes.AUTH_COOKIE},
                      status=200)
        responses.add(responses.GET, fakes.AUTH_URL_DEFAULT_TEST,
                      body=self.AUTH_RESP_TEXT, status=200)
        params = play.utils.get_url(sys.argv[2])
        play.play(params)
        observed = self.mock_plugin.resolved[2].getPath()
        expected = fakes.RESOLVED_URL.format(
            quote_plus(self.AUTH_RESP_TEXT, safe='~'),
            quote_plus(config.USER_AGENT))
        self.assertEqual(expected, observed)

    @mock.patch('os.path.isfile')
    @mock.patch('os.path.isdir')
    @mock.patch('io.open', new_callable=mock.mock_open)
    @mock.patch('time.time')
    @mock.patch('resources.lib.classes.utils.get_kodi_major_version')
    @mock.patch('xbmc.translatePath')
    @mock.patch('xbmcgui.ListItem')
    @mock.patch('sys.argv', ['plugin://plugin.video.abc_iview/', '5',
                             ('?action=program_list&url=%2fvideo%2fZW1939A025S'
                              '00&type=Program&house_number=ZW1939A025S00&capt'
                              'ions=True&title=foobar'),
                             'resume:false'])
    @responses.activate
    def test_play_captions(self, mock_listitem, mock_translate_path,
                           mock_version, mock_time,
                           mock_file, mock_isdir, mock_isfile):
        mock_listitem.side_effect = fakes.FakeListItem
        mock_translate_path.return_value = '/foo/bar/'
        mock_version.return_value = 15
        mock_time.return_value = 1565672000
        mock_isdir.return_value = True
        mock_isfile.return_value = False

        path = '/video/ZW1939A025S00'
        video_url = config.API_BASE_URL.format(path='/v2{0}'.format(path))
        url = '{0}&hdnea={1}'.format(fakes.EXPECTED_HLS_URL,
                                     self.AUTH_RESP_TEXT.decode('utf-8'))
        responses.add(responses.GET, video_url, body=self.VIDEO_JSON)
        responses.add(responses.GET, url, body='#EXTM3U',
                      headers={'Set-Cookie': fakes.AUTH_COOKIE},
                      status=200)
        responses.add(responses.GET, fakes.AUTH_URL_DEFAULT_TEST,
                      body=self.AUTH_RESP_TEXT, status=200)
        responses.add(responses.GET, fakes.EXPECTED_CAPTIONS_URL,
                      body=self.VTT_TEXT, status=200)
        params = play.utils.get_url(sys.argv[2])
        play.play(params)
        observed = self.mock_plugin.resolved[2].getPath()
        expected = fakes.RESOLVED_URL.format(
            quote_plus(self.AUTH_RESP_TEXT, safe='~'),
            quote_plus(config.USER_AGENT))
        self.assertEqual(expected, observed)
        mock_file.assert_called()
        handle = mock_file()
        handle.write.assert_called_once_with(fakes.EXPECTED_SRT_TEXT)
        observed = self.mock_plugin.resolved[2].subtitles
        expected = ['/foo/bar/subtitles.eng.srt']
        self.assertEqual(expected, observed)
