import datetime
import re
import time
import unicodedata
from builtins import str
from collections import OrderedDict
from functools import total_ordering

from future.moves.urllib.parse import parse_qsl, quote_plus, unquote_plus

from aussieaddonscommon import utils


def comp(x, y):
    return (x > y) - (x < y)


@total_ordering
class Series(object):

    def __init__(self):
        self.description = None
        self.num_episodes = 1
        self.series_houseno = None
        self.title = None
        self.thumb = None
        self.fanart = None
        self.type = 'Series'
        self.url = None
        self.dummy = None
        self.from_serieslist = False

    def __repr__(self):
        return self.title

    def __lt__(self, other):
        other_sort_title = getattr(other, 'get_sort_title', None)
        if callable(other_sort_title):
            return comp(self.get_sort_title(), other.get_sort_title()) < 0
        else:
            return comp(self.get_sort_title(), self.get_sort_title(other)) < 0

    def __eq__(self, other):
        other_sort_title = getattr(other, 'get_sort_title', None)
        if callable(other_sort_title):
            return comp(self.get_sort_title(), other.get_sort_title()) == 0
        else:
            return comp(self.get_sort_title(), self.get_sort_title(other)) == 0

    def get_sort_title(self, other=None):
        """Return a munged version of the title for sorting"""
        if other:
            sort_title = re.sub('[^A-Za-z0-9 ]+', '',
                                other.title).lower().replace('the ', '')
        else:
            sort_title = re.sub('[^A-Za-z0-9 ]+', '',
                                self.title).lower().replace('the ', '')
        return sort_title

    def get_title(self):
        """Return the program title, incl the Series X part on the end."""
        return utils.descape(self.title)

    def get_num_episodes(self):
        return self.num_episodes

    def get_list_title(self):
        """Return list title

        Return the program title with the number of episodes
        together suitable for the Kodi list
        """
        num_episodes = self.get_num_episodes()
        if num_episodes:
            return "{0} ({1})".format(self.get_title(), num_episodes)
        else:
            return self.get_title()

    def increment_num_episodes(self):
        self.num_episodes += 1

    def get_fanart(self):
        return self.fanart

    def get_thumb(self):
        return self.thumb

    def get_description(self):
        if self.description:
            return self.description

    def make_kodi_url(self, short=True):
        d_original = OrderedDict(
            sorted(self.__dict__.items(), key=lambda x: x[0]))
        d = d_original.copy()
        for key, value in d_original.items():
            if value != 0 and not value:
                d.pop(key)
                continue
            if short and key not in ['category', 'collection_id', 'title',
                                     'fanart', 'url', 'name', 'type', 'dummy',
                                     'num_episodes']:
                d.pop(key)
                continue
            if isinstance(value, str):
                d[key] = unicodedata.normalize(
                    'NFKD', value).encode('ascii', 'ignore').decode('utf-8')
        url = ''
        for key in d.keys():
            if isinstance(d[key], (str, bytes)):
                val = quote_plus(d[key])
            else:
                val = d[key]
            url += '&{0}={1}'.format(key, val)
        return url

    def parse_kodi_url(self, url):
        params = dict(parse_qsl(url))
        for item in params.keys():
            setattr(self, item, unquote_plus(params[item]))
        if self.num_episodes:
            self.num_episodes = int(self.num_episodes)


class Collect(Series):
    def __init__(self):
        super(Series, self).__init__()
        self.type = 'Collection'
        self.collection_id = None
        self.num_episodes = 0


@total_ordering
class Program(object):

    def __init__(self):
        self.title = None
        self.episode_title = None
        self.description = None
        self.series = None
        self.episode = None
        self.category = None
        self.keywords = []
        self.rating = 'PG'
        self.duration = None
        self.date = None
        self.thumb = None
        self.fanart = None
        self.url = None
        self.expire = None
        self.captions = False
        self.house_number = None
        self.type = 'Program'
        self.dummy = None
        self.stream_url = None
        self.captions_url = None
        self.failure_msg = None

    def __repr__(self):
        return self.title

    def __lt__(self, other):
        other_title = getattr(other, 'title', None)
        if other_title:
            return comp(self.title, other.title) < 0
        else:
            return comp(self.title, other) < 0

    def __eq__(self, other):
        other_title = getattr(other, 'title', None)
        if other_title:
            return comp(self.title, other.title) == 0
        else:
            return comp(self.title, other) == 0

    def parse_datetime(self, timestamp):
        """Parse timestamp into a datetime"""
        try:
            dt = time.mktime(time.strptime(timestamp, '%Y-%m-%d %H:%M:%S'))
            return datetime.datetime.fromtimestamp(dt)
        except Exception:
            utils.log_error("Couldn't parse timestamp: %s" % timestamp)
            raise

    def is_captions(self):
        return self.captions

    def get_title(self):
        """Get program title

        Return the program title, including the Series X part
        on the end.
        """
        return utils.descape(self.title)

    def get_episode_title(self):
        """Get episode title

        Return a string of the shorttitle entry, unless its not
        available, then we'll just use the program title instead.
        """
        if self.episode_title:
            return utils.descape(self.episode_title)

    def set_episode_title(self, title):
        self.episode_title = title

    def get_list_title(self):
        """Return a string of the title, nicely formatted for Kodi list"""
        title = self.get_title()

        if (self.get_season() and self.get_episode()):
            # Series and episode information
            title = "%s (S%02dE%02d)" % (title,
                                         self.get_season(),
                                         self.get_episode())
        elif self.get_episode():
            # Only episode information
            title = "%s (E%02d)" % (title, self.get_episode())
        elif self.get_season():
            # Only season information
            title = "%s (S%02d)" % (title, self.get_season())

        if self.get_episode_title():
            if title != self.get_episode_title():
                title = "%s: %s" % (title, self.get_episode_title())

        return title

    def get_description(self):
        """Get description

        Return a string the program description, after running it through
        the descape. Add the expires date to the end, if available
        """
        description = ""
        if self.description:
            description = self.description
        if self.expire:
            expire = "Expires: %s" % self.expire.strftime('%a, %d %b %Y')
            description = "%s\n%s" % (description, expire)
        return utils.descape(description)

    def get_category(self):
        """Return a string of the category. E.g. Comedy"""
        if self.category:
            return utils.descape(self.category)

    def get_rating(self):
        """Return a string of the rating. E.g. PG, MA"""
        if self.rating:
            return utils.descape(self.rating)

    def get_duration(self):
        """Return the duration"""
        if self.duration:
            version = utils.get_kodi_major_version()
            seconds = int(self.duration)
            if version >= 15:
                # Kodi v15 uses seconds
                return seconds
            else:
                # Older versions use minutes
                minutes = seconds // 60
                return minutes

    def get_date(self):
        """Get date

        Return a string of the date in the format 2010-02-28
        which is useful for XBMC labels.
        """
        if self.date:
            return self.date.strftime("%Y-%m-%d")

    def get_date_time(self):
        """Get date time

        Return string of the date/time in the format
        2016-09-08 10:00:00 which we can use to sort episodes
        """
        if self.date:
            return self.date.strftime("%Y-%m-%d %H:%M:%S")

    def get_year(self):
        """Return an integer of the year of publish date"""
        if self.date:
            return self.date.year

    def get_season(self):
        """Return an integer of the Series"""
        if self.series:
            return int(self.series)

    def set_season(self, season):
        self.series = season

    def get_episode(self):
        """Return an integer of the Episode"""
        if self.episode:
            return int(self.episode)

    def set_episode(self, episode):
        self.episode = episode

    def get_thumb(self):
        """Returns the thumbnail"""
        if self.thumb:
            return utils.descape(self.thumb)

    def get_fanart(self):
        """Returns the fanart"""
        if self.fanart:
            return utils.descape(self.fanart)

    def get_url(self):
        """Returns the video url"""
        if self.url:
            return utils.descape(self.url)

    def get_stream_url(self):
        return self.stream_url

    def get_captions_url(self):
        return self.captions_url

    def get_failure_msg(self):
        return self.failure_msg

    def get_expire(self):
        """Returns the expiry date"""
        if self.expire:
            return self.expire.strftime("%Y-%m-%d %H:%M:%S")

    def get_house_number(self):
        """Returns ABC's internal house number of the episode"""
        if self.house_number:
            return self.house_number

    def get_kodi_list_item(self):
        """Get XBMC list item

        Returns a dict of program information, in the format which
        Kodi requires for video metadata.
        """
        info_dict = {}
        if self.get_title():
            info_dict['tvshowtitle'] = self.get_title()
        if self.get_episode_title():
            info_dict['title'] = self.get_episode_title()
        if self.get_category():
            info_dict['genre'] = self.get_category()
        if self.get_description():
            info_dict['plot'] = self.get_description()
        if self.get_description():
            info_dict['plotoutline'] = self.get_description()
        if self.get_duration():
            info_dict['duration'] = self.get_duration()
        if self.get_year():
            info_dict['year'] = self.get_year()
        if self.get_date():
            info_dict['aired'] = self.get_date()
        if self.get_season():
            info_dict['season'] = self.get_season()
        if self.get_episode():
            info_dict['episode'] = self.get_episode()
        if self.get_rating():
            info_dict['mpaa'] = self.get_rating()
        return info_dict

    def get_kodi_audio_stream_info(self):
        """Return an audio stream info dict"""
        info_dict = {}
        # This information may be incorrect
        info_dict['codec'] = 'aac'
        info_dict['language'] = 'en'
        info_dict['channels'] = 2
        return info_dict

    def get_kodi_video_stream_info(self):
        """Return a video stream info dict"""
        info_dict = {}
        if self.get_duration():
            info_dict['duration'] = self.get_duration()

        # This information may be incorrect
        info_dict['codec'] = 'h264'
        info_dict['width'] = '1024'
        info_dict['height'] = '576'

        return info_dict

    def set_date(self, timestamp):
        if timestamp:
            self.date = self.parse_datetime(timestamp)

    def set_expire(self, timestamp):
        if timestamp:
            self.expire = self.parse_datetime(timestamp)

    def make_kodi_url(self, short=True):
        d_original = OrderedDict(
            sorted(self.__dict__.items(), key=lambda x: x[0]))
        d = d_original.copy()
        for key, value in d_original.items():
            if not value:
                d.pop(key)
                continue
            if short and key not in ['house_number', 'url', 'type']:
                d.pop(key)
                continue
            if isinstance(value, str):
                d[key] = unicodedata.normalize(
                    'NFKD', value).encode('ascii', 'ignore').decode('utf-8')
        url = ''
        for key in d.keys():
            if isinstance(d[key], (str, bytes)):
                val = quote_plus(d[key])
            else:
                val = d[key]
            url += '&{0}={1}'.format(key, val)
        return url

    def parse_kodi_url(self, url):
        params = dict(parse_qsl(url))
        for item in params.keys():
            setattr(self, item, unquote_plus(params[item]))
        if getattr(self, 'captions', None) == 'True':
            self.captions = True
        if getattr(self, 'date', None):
            self.date = self.parse_datetime(self.date)
        if getattr(self, 'expire', None):
            self.expire = self.parse_datetime(self.expire)
