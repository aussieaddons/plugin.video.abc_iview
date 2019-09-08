from __future__ import absolute_import, unicode_literals

from collections import OrderedDict
from datetime import datetime

try:
    import mock
except ImportError:
    import unittest.mock as mock

import testtools

import resources.lib.classes as classes
from resources.tests.fakes import fakes


class ClassesSeriesTests(testtools.TestCase):

    def test_get_sort_title(self):
        s = classes.Series()
        s.title = 'The Foo'
        observed = s.get_sort_title()
        expected = 'foo'
        self.assertEqual(expected, observed)

    def test_get_title(self):
        s = classes.Series()
        s.title = '&lt;spam&amp;eggs&gt;'
        observed = s.get_title()
        expected = '<spam&eggs>'
        self.assertEqual(expected, observed)

    def test_get_list_title(self):
        s = classes.Series()
        s.title = 'Foo Bar'
        observed = s.get_list_title()
        expected = 'Foo Bar (1)'
        self.assertEqual(expected, observed)


class ClassesProgramTests(testtools.TestCase):

    def test_get_title(self):
        p = classes.Program()
        p.title = '&lt;spam&amp;eggs&gt;'
        observed = p.get_title()
        expected = '<spam&eggs>'
        self.assertEqual(expected, observed)

    def test_get_episode_title(self):
        p = classes.Program()
        p.episode_title = '&lt;spam&amp;eggs&gt;'
        observed = p.get_episode_title()
        expected = '<spam&eggs>'
        self.assertEqual(expected, observed)

    def test_get_episode_title_blank(self):
        p = classes.Program()
        observed = p.get_episode_title()
        expected = None
        self.assertEqual(expected, observed)

    def test_get_list_title_season_episode(self):
        p = classes.Program()
        p.title = 'Foobar'
        p.series = '3'
        p.episode = '10'
        observed = p.get_list_title()
        expected = 'Foobar (S03E10)'
        self.assertEqual(expected, observed)

    def test_get_list_title_season_episode_title(self):
        p = classes.Program()
        p.title = 'Foobar'
        p.series = '3'
        p.episode_title = 'Revenge of Spam'
        observed = p.get_list_title()
        expected = 'Foobar (S03): Revenge of Spam'
        self.assertEqual(expected, observed)

    def test_get_list_title_episode(self):
        p = classes.Program()
        p.title = 'Foobar'
        p.episode = '10'
        observed = p.get_list_title()
        expected = 'Foobar (E10)'
        self.assertEqual(expected, observed)

    def test_get_list_title_season(self):
        p = classes.Program()
        p.title = 'Foobar'
        p.series = '3'
        observed = p.get_list_title()
        expected = 'Foobar (S03)'
        self.assertEqual(expected, observed)

    def test_get_description(self):
        p = classes.Program()
        p.description = 'Foo kills Bar'
        p.expire = datetime(2019, 8, 13)
        observed = p.get_description()
        expected = 'Foo kills Bar\nExpires: Tue, 13 Aug 2019'
        self.assertEqual(expected, observed)

    @mock.patch('resources.lib.classes.utils.get_kodi_major_version')
    def test_get_duration_isengard(self, mock_version):
        mock_version.return_value = 15
        p = classes.Program()
        p.duration = '903'
        observed = p.get_duration()
        expected = 903
        self.assertEqual(expected, observed)

    @mock.patch('resources.lib.classes.utils.get_kodi_major_version')
    def test_get_duration_helix(self, mock_version):
        mock_version.return_value = 14
        p = classes.Program()
        p.duration = '903'
        observed = p.get_duration()
        expected = 15
        self.assertEqual(expected, observed)

    def test_get_date(self):
        p = classes.Program()
        p.date = datetime(2019, 8, 13)
        observed = p.get_date()
        expected = '2019-08-13'
        self.assertEqual(expected, observed)

    def test_get_date_time(self):
        p = classes.Program()
        p.date = datetime(2019, 8, 13, 20, 1, 23)
        observed = p.get_date_time()
        expected = '2019-08-13 20:01:23'
        self.assertEqual(expected, observed)

    def test_get_expire(self):
        p = classes.Program()
        p.expire = datetime(2019, 8, 13, 0, 0, 0)
        observed = p.get_expire()
        expected = '2019-08-13 00:00:00'
        self.assertEqual(expected, observed)

    @mock.patch('resources.lib.classes.utils.get_kodi_major_version')
    def test_get_kodi_list_item(self, mock_version):
        mock_version.return_value = 15
        p = classes.Program()
        p.title = 'Foo'
        p.episode_title = 'Return of Foo'
        p.series = '2'
        p.duration = '100'
        p.date = datetime(2019, 8, 13, 20, 1, 23)
        observed = p.get_kodi_list_item()
        expected = fakes.INFO_DICT
        self.assertEqual(expected, observed)

    def test_set_datetime_objects(self):
        expire = '2019-09-12 10:01:36'
        p = classes.Program()
        p.set_expire(expire)
        observed = p.expire
        expected = datetime(2019, 9, 12, 10, 1, 36)
        self.assertEqual(expected, observed)

    def test_set_datetime_strings(self):
        expire = '2019-09-12 10:01:36'
        p = classes.Program()
        p.set_expire(expire)
        observed = p.expire
        self.assertEqual(expire, str(observed))

    def test_make_kodi_url(self):
        p = classes.Program()
        attrs = OrderedDict(
            sorted(fakes.PROGRAM_ATTRS.items(), key=lambda x: x[0]))
        for k, v in attrs.items():
            setattr(p, k, v)
        p.__dict__.pop('date')  # do we still need the date attrib?
        observed = p.make_kodi_url()
        self.assertEqual(fakes.PROGRAM_URL, observed)

    def test_parse_kodi_url(self):
        p = classes.Program()
        p.parse_kodi_url(fakes.PROGRAM_URL)
        p.__dict__.pop('date')  # do we still need the date attrib?
        observed = p.make_kodi_url()
        self.assertEqual(fakes.PROGRAM_URL, observed)