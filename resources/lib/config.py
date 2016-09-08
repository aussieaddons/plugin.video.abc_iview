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

user_agent = [('User-Agent', 'Android SDK HW (5.31.0; 6.0; htc_himauhl; arm64-v8a)')]
secret = 'android.content.res.Resources'

base_url     = 'http://iview.abc.net.au'
config_url   = 'http://iview.abc.net.au/api/navigation/mobile/2/?device=android-mobile&'
auth_url     = '/auth/hls/sign?'
index_url    = 'http://iview.abc.net.au/api/index?device=android-mobile&fields=seriesTitle,episodeCount,href'
feed_url     = 'http://iview.abc.net.au/api/{0}?device=android-mobile&sort=az'





