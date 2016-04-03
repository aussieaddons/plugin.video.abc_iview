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

import os
import version

NAME = 'ABC iView'
ADDON_ID = 'plugin.video.abc_iview'
VERSION = version.VERSION

GITHUB_API_URL = 'https://api.github.com/repos/andybotting/xbmc-addon-abc-iview'
ISSUE_API_URL = GITHUB_API_URL + '/issues'
ISSUE_API_AUTH = 'eGJtY2JvdDo1OTQxNTJjMTBhZGFiNGRlN2M0YWZkZDYwZGQ5NDFkNWY4YmIzOGFj'
GIST_API_URL = 'https://api.github.com/gists'

api_version = 383

# os.uname() is not available on Windows, so we make this optional.
try:
    uname = os.uname()
    os_string = ' (%s %s %s)' % (uname[0], uname[2], uname[4])
except AttributeError:
    os_string = ''

user_agent = '%s add-on for XBMC/Kodi %s%s' % (NAME, VERSION, os_string)

base_url     = 'http://www.abc.net.au/iview/'
config_url   = 'http://www.abc.net.au/iview/xml/config.xml?r=%d' % api_version
auth_url     = 'http://tviview.abc.net.au/iview/auth/?v2'
programs_url = 'http://iview.abc.net.au/api/search/programs'
feed_url     = 'https://tviview.abc.net.au/iview/feed/lg/'
subtitle_url = 'http://cdn.iview.abc.net.au/cc/'

series_url   = 'http://www.abc.net.au/iview/api/series_mrss.htm?id=%s'
redirect_url = 'http://iview.abc.net.au/redirect/legacy/?url='

akamai_fallback_server = 'rtmp://cp53909.edgefcs.net/ondemand'
akamai_playpath_prefix = 'flash/playback/_definst_/'

# Used for "SWF verification", a stream obfuscation technique
swf_hash    = '96cc76f1d5385fb5cda6e2ce5c73323a399043d0bb6c687edd807e5c73c42b37'
swf_size    = '2122'
swf_url     = 'http://www.abc.net.au/iview/images/iview.jpg'

