from __future__ import absolute_import, unicode_literals

import io
import json
import os

import testtools

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
        with open(os.path.join(cwd, 'fakes/json/collection3.json'), 'rb') as f:
            self.COLLECTION3_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/show.json'), 'rb') as f:
            self.SHOW_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/show_empty.json'), 'rb') as f:
            self.SHOW_EMPTY_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/show_multiseries.json'),
                  'rb') as f:
            self.SHOW_MULTISERIES_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_ss.json'), 'rb') as f:
            self.VIDEO_JSON = io.BytesIO(f.read()).read()
        with open(os.path.join(cwd, 'fakes/json/video_tb.json'), 'rb') as f:
            self.VIDEO_JSON_NA = io.BytesIO(f.read()).read()

    def test_get_categories(self):
        category_list = parse.parse_categories(self.NAV_JSON)
        expected_len = 17
        observed_len = len(category_list)
        self.assertEqual(expected_len, observed_len)

    def test_get_programme_from_feed(self):
        observed = parse.parse_programme_from_feed(self.COLLECTION_JSON, {})
        self.assertEqual([x.get('title') for x in
                          json.loads(self.COLLECTION_JSON).get('items')],
                         [x.title for x in observed])

    def test_get_programme_from_feed_missing_show_display_title(self):
        observed = parse.parse_programme_from_feed(self.COLLECTION3_JSON, {})
        self.assertEqual([x.get('title') for x in
                          json.loads(self.COLLECTION3_JSON).get('items')],
                         [x.title for x in observed])

    def test_get_series_from_feed_empty(self):
        observed = parse.parse_programs_from_feed(self.SHOW_EMPTY_JSON)
        self.assertEqual(0, len(observed))

    def test_get_series_from_feed(self):
        observed = parse.parse_programs_from_feed(self.SHOW_JSON)
        json_data = json.loads(self.SHOW_JSON)['_embedded']['selectedSeries'][
            '_embedded'].get('videoEpisodes')
        expected_episode_titles = [x.get('title') for x in json_data]
        observed_episode_titles = [x.episode_title for x in observed]
        self.assertEqual(expected_episode_titles, observed_episode_titles)

    def test_get_series_from_feed_with_extra_series(self):
        observed = parse.parse_programs_from_feed(self.SHOW_MULTISERIES_JSON)
        json_data = json.loads(self.SHOW_MULTISERIES_JSON)
        current_series_data = json_data['_embedded']['selectedSeries'][
            '_embedded'].get('videoEpisodes')
        series_json_data = json_data['_embedded']['seriesList']
        expected_titles = [x.get('title') for x in current_series_data]
        expected_titles.extend(
            [x.get('title') for x in series_json_data if x.get('id') !=
             json_data['_embedded']['selectedSeries']['id']])
        observed_titles = [
            x.episode_title for x in observed if x.type == 'Program']
        observed_titles.extend(
            [x.title for x in observed if x.type == 'Series'])
        self.assertEqual(expected_titles, observed_titles)

    def test_parse_collections_from_feed(self):
        observed = parse.parse_collections_from_feed(self.CHANNEL_JSON, {})
        self.assertEqual(17, len(observed))
        self.assertEqual('ABC KIDS Favourites', observed[0].get_title())

    def test_parse_stream_from_json(self):
        data = json.loads(self.VIDEO_JSON)
        p = parse.parse_stream_from_json(data)
        self.assertEqual(p.get_list_title(),
                         'Sesame Street: Mechanics in Space')
        self.assertEqual(p.get_date(), '2019-08-13')
