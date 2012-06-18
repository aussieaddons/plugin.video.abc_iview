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

import os

NAME = 'ABC iView'
VERSION = '1.2.0'

api_version = 383

# os.uname() is not available on Windows, so we make this optional.
try:
	uname = os.uname()
	os_string = ' (%s %s %s)' % (uname[0], uname[2], uname[4])
except AttributeError:
	os_string = ''

user_agent = '%s plugin for XBMC %s%s' % (NAME, VERSION, os_string)

base_url   = 'http://www.abc.net.au/iview/'
config_url = 'http://www.abc.net.au/iview/xml/config.xml?r=%d' % api_version
auth_url   = 'http://tviview.abc.net.au/iview/auth/?v2'
series_url = 'http://www.abc.net.au/iview/api/series_mrss.htm?id=%s'

akamai_playpath_prefix = 'flash/playback/_definst_/'

# Used for "SWF verification", a stream obfuscation technique
swf_hash    = '96cc76f1d5385fb5cda6e2ce5c73323a399043d0bb6c687edd807e5c73c42b37'
swf_size    = '2122'
swf_url     = 'http://www.abc.net.au/iview/images/iview.jpg'

