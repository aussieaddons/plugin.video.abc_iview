from __future__ import absolute_import, unicode_literals

import io
import json
import os

try:
    import mock
except ImportError:
    import unittest.mock as mock

import responses

import testtools

import resources.lib.config as config
import resources.lib.parse as parse


class ParseTests(testtools.TestCase):

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


    def test_get_categories(self):
        category_list = parse.parse_categories(self.NAV_JSON)
        expected_len = 17
        observed_len = len(category_list)
        self.assertEqual(expected_len, observed_len)

    @responses.activate
    def test_get_programme_from_feed(self):
        collection_path = '/collection/1962'
        collection_url = config.API_BASE_URL.format(
            path='/v2{0}'.format(collection_path))
        responses.add(responses.GET, collection_url, body=self.COLLECTION_JSON)
        observed = parse.parse_programme_from_feed(self.CHANNEL_JSON)
        import json
        self.assertEqual([x.get('title') for x in
                          json.loads(self.COLLECTION_JSON).get('items')],
                         [x.title for x in observed])

    def test_get_series_from_feed(self):
        observed = parse.parse_programs_from_feed(self.SHOW_JSON)
        json_data = json.loads(self.SHOW_JSON)['_embedded']['selectedSeries'][
            '_embedded'].get('videoEpisodes')
        expected_episode_titles = [x.get('title') for x in json_data]
        observed_episode_titles = [x.episode_title for x in observed]
        self.assertEqual(expected_episode_titles, observed_episode_titles)