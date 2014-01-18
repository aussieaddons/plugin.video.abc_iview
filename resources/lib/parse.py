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

import comm
import config
import classes
import utils
import sys
import re
import datetime
import time

# Try importing default modules, but if that doesn't work
# we might be old platforms with bundled deps
try:
	from BeautifulSoup import BeautifulStoneSoup
except ImportError:
	from deps.BeautifulSoup import BeautifulStoneSoup

# Try importing default modules, but if that doesn't work
# we might be old platforms with bundled deps
try:
	import simplejson as json
except ImportError:
	try:
		import deps.simplejson as json
	except ImportError:
		import json


def parse_config(soup):
	"""There are lots of goodies in the config we get back from the ABC.
		In particular, it gives us the URLs of all the other XML data we
		need.
	"""

	soup = soup.replace('&amp;', '&#38;')

	xml = BeautifulStoneSoup(soup)

	# should look like "rtmp://cp53909.edgefcs.net/ondemand"
	# Looks like the ABC don't always include this field.
	# If not included, that's okay -- ABC usually gives us the server in the auth result as well.
	rtmp_url = xml.find('param', attrs={'name':'server_streaming'}).get('value')
	rtmp_chunks = rtmp_url.split('/')

	return {
		'rtmp_url'  : rtmp_url,
		'rtmp_host' : rtmp_chunks[2],
		'rtmp_app'  : rtmp_chunks[3],
		'api_url' : xml.find('param', attrs={'name':'api'}).get('value'),
		'categories_url' : xml.find('param', attrs={'name':'categories'}).get('value'),
	}


def parse_auth(soup, iview_config):
	"""	There are lots of goodies in the auth handshake we get back,
		but the only ones we are interested in are the RTMP URL, the auth
		token, and whether the connection is unmetered.
	"""

	xml = BeautifulStoneSoup(soup)

	# should look like "rtmp://203.18.195.10/ondemand"
	try:
		rtmp_url = xml.find('server').string

		# at time of writing, either 'Akamai' (usually metered) or 'Hostworks' (usually unmetered)
		stream_host = xml.find('host').string

		playpath_prefix = ''
		if stream_host == 'Akamai':
			playpath_prefix = config.akamai_playpath_prefix

		if rtmp_url is not None:
			# Being directed to a custom streaming server (i.e. for unmetered services).
			# Currently this includes Hostworks for all unmetered ISPs except iiNet.
			rtmp_chunks = rtmp_url.split('/')
			rtmp_host = rtmp_chunks[2]
			rtmp_app = rtmp_chunks[3]
		else:
			# We are a bland generic ISP using Akamai, or we are iiNet.
			rtmp_url = iview_config['rtmp_url']
			rtmp_host = iview_config['rtmp_host']
			rtmp_app = iview_config['rtmp_app']

		token = xml.find("token").string
		token = token.replace('&amp;', '&') # work around BeautifulSoup bug
	except:
		exc_type, exc_value, exc_traceback = sys.exc_info()
		raise Exception("iView handshake error: %s" % exc_value)

	return {
		'rtmp_url'        : rtmp_url,
		'rtmp_host'       : rtmp_host,
		'rtmp_app'        : rtmp_app,
		'playpath_prefix' : playpath_prefix,
		'token'           : token,
		'free'            : (xml.find("free").string == "yes")
	}

def parse_index(soup):
	"""	This function parses the index, which is an overall listing
		of all programs available in iView. The index is divided into
		'series' and 'items'. Series are things like 'beached az', while
		items are things like 'beached az Episode 8'.
	"""
	series_list = []
	index = json.loads(soup)
	for series in index:
		new_series = classes.Series()

		#{u'a': u'9995608',
		#	u'b': u'Wildscreen Series 1',
		#	u'e': u'shopdownload',
		#	u'f': [{u'a': u'9995608',
		#			u'f': u'2010-05-30 00:00:00',
		#			u'g': u'2010-07-17 00:00:00'}]
		#}

		new_series.id = series['a']
		new_series.title = series['b']
		new_series.keywords = series['e'].split(" ")
		new_series.num_episodes = int(len(series['f']))
		new_series.description = series['c']
		new_series.thumbnail = series['d']

		# Only include a program if isn't a 'Shop Download'
		if new_series.has_keyword("shopdownload"):
			utils.log("Skipping shopdownload: %s" % new_series.title)
			continue

		if new_series.title == "ABC News 24":
			utils.log("Skipping: %s" % new_series.title)
			continue

		if new_series.num_episodes > 0:
			utils.log("Found series: %s" % (new_series.get_list_title()))
			series_list.append(new_series)

	return series_list

def parse_categories(soup):
	categories_list = []

	"""
	<category id="pre-school" genre="true">
		<name>ABC 4 Kids</name>
	</category>
	"""

	# This next line is the magic to make recursive=False work (wtf?)
	BeautifulStoneSoup.NESTABLE_TAGS["category"] = []
	xml = BeautifulStoneSoup(soup)

	# Get all the top level categories, except the alphabetical ones
	for cat in xml.find('categories').findAll('category', recursive=False):

		id = cat.get('id')
		if cat.get('index') or id == 'index':
			continue

		item = {}
		item['keyword'] = id
		item['name']    = cat.find('name').string;

		categories_list.append(item);

	return categories_list

def parse_series_items(soup):
	series_json = json.loads(soup)

	if series_json[0]['a'] == '9900019':
		if len(series_json) == 1:
			index = 0
		else:
			index = 1
	else:
		index = 0

	programs_list = []

	series_id = series_json[index]['a']
	# Roary The Racing Car Series 2
	series_title = series_json[index]['b']
	series_thumb = series_json[index]['d']

	for item in series_json[index]['f']:

		new_program = classes.Program()
		new_program.id = item.get('a')

		# Let's try and parse the title apart
		title_string = item.get('b')

		# Roary The Racing Car Series 2 Episode 25 Home Is Where The Hatch Is
		title_match = re.search('^(?P<title>.*)\s+[Ss]eries\s?(?P<series>\w+)\s[Ee]pisode\s?(?P<episode>\d+)\s(?P<episode_title>.*)$', title_string)
		if not title_match:
			# At The Movies Series 8 Episode 13
			title_match = re.search('^(?P<title>.*)\s+[Ss]eries\s?(?P<series>\w+)\s[Ee]pisode\s?(?P<episode>\d+)$', title_string)
		if not title_match:
			# Astro Boy Episode 34 Shape Shifter
			title_match = re.search('^(?P<title>.*)\s[Ee]pisode\s?(?P<episode>\d+)\s(?P<episode_title>.*)$', title_string)
		if not title_match:
			#Country Town Rescue Episode 5
			title_match = re.search('^(?P<title>.*)\s[Ee]pisode\s?(?P<episode>\d+)$', title_string)
		if not title_match:
			# 7.30 10/05/12
			title_match = re.search('^(?P<title>.*)\s(?P<episode_title>\d+/\d+/\d+)$', title_string)
		if not title_match:
			# 7.30 Budget Special Report 2012 Right Of Reply Special Edition
			title_match = re.search('^(?P<title>.* 2012)\s(?P<episode_title>.*)$', title_string)
		if not title_match:
			# Bananas In Pyjamas Morgan's Cafe
			title_match = re.search("^(?P<title>%s)\s(?P<episode_title>.*)$" % series_title, title_string)
		if not title_match:
			# Anything else
			title_match = re.search("^(?P<title>.*)$", title_string)

		title_parts = title_match.groupdict()

		new_program.title         = title_parts.get('title')
		new_program.episode_title = title_parts.get('episode_title')
		new_program.series        = title_parts.get('series')
		new_program.episode       = title_parts.get('episode')

		new_program.description   = item.get('d')
		new_program.url           = item.get('n')

		new_program.livestream    = item.get('r')
		new_program.thumbnail     = item.get('s')

		new_program.duration      = item.get('j')

		temp_date = item.get('f')
		try:
			timestamp = time.mktime(time.strptime(temp_date, '%Y-%m-%d %H:%M:%S'))
		except:
			timestamp = time.mktime(time.strptime(temp_date, '%Y-%m-%d'))
		new_program.date = datetime.date.fromtimestamp(timestamp)

		programs_list.append(new_program)

	return programs_list
