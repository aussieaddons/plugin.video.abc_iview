#
#	ABC iView XBMC Plugin
#	Copyright (C) 2012 Andy Botting
#
#  This plugin includes from from python-iview
#  Copyright (C) 2009-2012 by Jeremy Visser <jeremy@visser.name>
#
#	This plugin is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This plugin is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this plugin. If not, see <http://www.gnu.org/licenses/>.
#

import re
import utils
import datetime
import urllib
import time

class Series(object):

	def __init__(self):
		pass

	def __repr__(self):
		return self.title

	def __cmp__(self, other):
		return cmp(self.get_sort_title(), other.get_sort_title())

	def get_sort_title(self):
		""" Return a munged version of the title which
			forces correct sorting behaviour.
		"""
		sort_title = self.title.lower()
		sort_title = sort_title.replace('the ', '')
		return sort_title

	def get_title(self):
		""" Return the program title, including the Series X part
			on the end.
		"""
		return utils.descape(self.title)

	def get_list_title(self):
		""" Return the program title with the number of episodes
			together for the XBMC list
		"""
		return "%s (%d)" % (self.get_title(), self.get_num_episodes())

	def get_season(self):
		""" Return an integer of the Series, discovered by a regular
			expression from the orginal title, unless its not available,
			then a 0 will be returned.
		"""
		season = re.search('^.* Series (?P<season>\d+)$', self.get_title())
		if title is None:
			return 0
		return int(series.group('season'))

	def get_num_episodes(self):
		return self.num_episodes

	def get_keywords(self):
		""" Return a list of keywords
		"""
		return self.keywords

	def get_thumbnail(self):
		return self.thumbnail

	def get_description(self):
		return self.description

	def has_keyword(self, keyword):
		""" Returns true if a keyword is found
		"""
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
		self.category = 'Unknown'
		self.keywords = []
		self.rating = 'PG'
		self.duration = '0'
		self.date = datetime.datetime.now()
		self.thumbnail = None

	def __repr__(self):
		return self.title

	def __cmp__(self, other):
		return cmp(self.title, other.title)

	def get_title(self):
		""" Return the program title, including the Series X part
			on the end.
		"""
		return utils.descape(self.title)

	def get_episode_title(self):
		""" Return a string of the shorttitle entry, unless its not 
			available, then we'll just use the program title instead.
		"""
		if self.episode_title:
			return utils.descape(self.episode_title)

	def get_list_title(self):
		""" Return a string of the title, nicely formatted for XBMC list
		"""
		title = self.get_title()

		if (self.get_season() and self.get_episode()):
			# Series and episode information
			title = "%s (S%02dE%02d)" % (title, self.get_season(), self.get_episode())
		else:
			if self.get_episode():
				# Only episode information
				title = "%s (E%02d)" % (title, self.get_episode())
			else:
				if not self.get_episode_title():
					# Date only, no episode information or episode title
					title = "%s (%s)" % (title, self.get_date())

		if self.get_episode_title():
			title = "%s: %s" % (title, self.get_episode_title())

		return title

	def get_description(self):
		""" Return a string the program description, after running it through
			the descape.
		"""
		return utils.descape(self.description)

	def get_category(self):
		""" Return a string of the category. E.g. Comedy
		"""
		return utils.descape(self.category)

	def get_rating(self):
		""" Return a string of the rating. E.g. PG, MA
		"""
		return utils.descape(self.category)

	def get_duration(self):
		""" Return a string representing the duration of the program.
			E.g. 00:30 (30 minutes)
		"""
		seconds = int(self.duration)
		hours = seconds / 3600
		seconds -= 3600*hours
		minutes = seconds / 60
		return "%02d:%02d" % (hours, minutes)

	def get_date(self):
		""" Return a string of the date in the format 2010-02-28
			which is useful for XBMC labels.
		"""
		return self.date.strftime("%Y-%m-%d")

	def get_year(self):
		""" Return an integer of the year of publish date
		"""
		return self.date.year

	def get_season(self):
		""" Return an integer of the Series
		"""
		if self.series:
			return int(self.series)

	def get_episode(self):
		""" Return an integer of the Episode
		"""
		if self.episode:
			return int(self.episode)

	def get_thumbnail(self):
		""" Returns the thumbnail
		"""
		return utils.descape(self.thumbnail)

	def get_xbmc_list_item(self):
		""" Returns a dict of program information, in the format which
			XBMC requires for video metadata.
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

	def make_xbmc_url(self):
		""" Returns a string which represents the program object, but in
			a format suitable for passing as a URL.
		"""
		d = {}
		if self.id:            d['id'] = self.id
		if self.title:         d['title'] = self.title
		if self.episode_title: d['episode_title'] = self.episode_title
		if self.description:   d['description'] = self.description
		if self.duration:      d['duration'] = self.duration
		if self.category:      d['category'] = self.category
		if self.rating:        d['rating'] = self.rating
		if self.date:          d['date'] = self.date.strftime("%Y-%m-%d %H:%M:%S")
		if self.thumbnail:     d['thumbnail'] = self.thumbnail
		if self.url:           d['url'] = self.url

		return utils.make_url(d)


	def parse_xbmc_url(self, string):
		""" Takes a string input which is a URL representation of the 
		   program object
		"""
		d = utils.get_url(string)
		self.id            = d.get('id')
		self.title         = d.get('title')
		self.episode_title = d.get('episode_title')
		self.description   = d.get('description')
		self.duration      = d.get('duration')
		self.category      = d.get('category')
		self.rating        = d.get('rating')
		self.url           = d.get('url')
		self.thumbnail     = urllib.unquote_plus(d.get('thumbnail'))
		if d.has_key('date'):
		   timestamp = time.mktime(time.strptime(d['date'], '%Y-%m-%d %H:%M:%S'))
		   self.date = datetime.date.fromtimestamp(timestamp)

