#
#  ABC iView XBMC Addon
#  Copyright (C) 2012 Andy Botting
#
#  This addon includes code from python-iview
#  Copyright (C) 2009-2012 by Jeremy Visser <jeremy@visser.name>
#
#  This addon is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This addon is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this addon. If not, see <http://www.gnu.org/licenses/>.
#

import datetime
import time
import urllib

from aussieaddonscommon import utils


class Series(object):

    def __init__(self):
        self.description = None
        self.num_episodes = 1
        self.thumbnail = None
        self.series_houseno = None

    def __repr__(self):
        return self.title

    def __cmp__(self, other):
        return cmp(self.get_sort_title(), other.get_sort_title())

    def get_sort_title(self):
        """Return a munged version of the title for sorting"""
        sort_title = self.title.lower()
        sort_title = sort_title.replace('the ', '')
        return sort_title

    def get_title(self):
        """Return the program title, incl the Series X part on the end."""
        return utils.descape(self.title)

    def get_list_title(self):
        """Return list title

        Return the program title with the number of episodes
        together suitable for the Kodi list
        """
        return "%s (%d)" % (self.get_title(), self.get_num_episodes())

    def increment_num_episodes(self):
        self.num_episodes += 1

    def get_num_episodes(self):
        return self.num_episodes

    def get_keywords(self):
        """Return a list of keywords"""
        if self.keywords:
            return self.keywords

    def get_thumbnail(self):
        if self.thumbnail:
            return self.thumbnail

    def get_description(self):
        if self.description:
            return self.description

    def has_keyword(self, keyword):
        """Returns true if a keyword is found"""
        for kw in self.keywords:
            if kw == keyword:
                return True
        return False


class Program(object):

    def __init__(self):
        self.id = -1
        self.title = None
        self.episode_title = None
        self.description = None
        self.series = None
        self.episode = None
        self.category = None
        self.keywords = []
        self.rating = 'PG'
        self.duration = None
        self.date = datetime.datetime.now()
        self.thumbnail = None
        self.url = None
        self.expire = None
        self.subtitle_url = None
        self.house_number = None
        self.hq = None

    def __repr__(self):
        return self.title

    def __cmp__(self, other):
        return cmp(self.title, other.title)

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
                minutes = seconds / 60
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

    def get_episode(self):
        """Return an integer of the Episode"""
        if self.episode:
            return int(self.episode)

    def get_thumbnail(self):
        """Returns the thumbnail"""
        if self.thumbnail:
            return utils.descape(self.thumbnail)

    def get_url(self):
        """Returns the video url"""
        if self.url:
            return utils.descape(self.url)

    def get_expire(self):
        """Returns the expiry date"""
        if self.expire:
            return self.expire.strftime("%Y-%m-%d %h:%m:%s")

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
        if self.hq:
            info_dict['codec'] = 'h264'
            info_dict['width'] = '1024'
            info_dict['height'] = '576'
        else:
            info_dict['codec'] = 'h264'
            info_dict['width'] = '640'
            info_dict['height'] = '360'
        return info_dict

    def make_xbmc_url(self):
        """Make XBMC url

        Returns a string which represents the program object, but in
        a format suitable for passing as a URL.
        """
        d = {}
        if self.id:
            d['id'] = self.id
        if self.title:
            d['title'] = self.title
        if self.episode_title:
            d['episode_title'] = self.episode_title
        if self.description:
            d['description'] = self.description
        if self.duration:
            d['duration'] = self.duration
        if self.category:
            d['category'] = self.category
        if self.rating:
            d['rating'] = self.rating
        if self.date:
            d['date'] = self.date.strftime("%Y-%m-%d %H:%M:%S")
        if self.thumbnail:
            d['thumbnail'] = self.thumbnail
        if self.url:
            d['url'] = self.url
        if self.subtitle_url:
            d['subtitle_url'] = self.subtitle_url
        if self.house_number:
            d['house_number'] = self.house_number
        if self.hq:
            d['hq'] = self.hq
        return utils.make_url(d)

    def parse_xbmc_url(self, string):
        """Parse XBMC URL

        Takes a string input which is a URL representation of the
        program object
        """
        d = utils.get_url(string)
        self.id = d.get('id')
        self.title = d.get('title')
        self.episode_title = d.get('episode_title')
        self.description = d.get('description')
        self.duration = d.get('duration')
        self.category = d.get('category')
        self.rating = d.get('rating')
        self.url = d.get('url')
        self.thumbnail = urllib.unquote_plus(d.get('thumbnail'))
        self.subtitle_url = d.get('subtitle_url')
        self.house_number = d.get('house_number')
        self.hq = d.get('hq')
        if 'date' in d:
            timestamp = time.mktime(time.strptime(d['date'],
                                                  '%Y-%m-%d %H:%M:%S'))
            self.date = datetime.date.fromtimestamp(timestamp)
