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
# flake8: noqa

NAME = 'ABC iView'
ADDON_ID = 'plugin.video.abc_iview'

GITHUB_API_URL = 'https://api.github.com/repos/andybotting/xbmc-addon-abc-iview'
ISSUE_API_URL = GITHUB_API_URL + '/issues'
ISSUE_API_AUTH = 'eGJtY2JvdDo1OTQxNTJjMTBhZGFiNGRlN2M0YWZkZDYwZGQ5NDFkNWY4YmIzOGFj'
GIST_API_URL = 'https://api.github.com/gists'

USER_AGENT = 'Mozilla/5.0 (PlayStation 4) AppleWebKit/531.3 (KHTML, like Gecko) SCEE/1.0 Nuanti/2.0'
HEADERS = {'User-Agent': USER_AGENT,
           'Origin': 'http://tv.iview.abc.net.au',
           'Referer': 'http://tv.iview.abc.net.au/playstation.php'}
SECRET = 'android.content.res.Resources'

BASE_URL = 'http://iview.abc.net.au'
CONFIG_URL = 'http://iview.abc.net.au/api/navigation/mobile/2/?device=hbb&hbr=1'
AUTH_URL = '/auth/hls/sign?'
INDEX_URL = 'http://iview.abc.net.au/api/index?device=hbb&hbr=1&fields=seriesTitle,episodeCount,href'
FEED_URL = 'http://iview.abc.net.au/api/{0}?device=hbb&hbr=1&sort=az'

CATEGORIES = {'arts': 'channel/abcarts',
              'docs': 'category/docs',
              'comedy': 'category/comedy',
              'drama': 'category/drama',
              'education': 'category/education',
              'abc4kids': 'channel/abc4kids',
              'indigenous': 'category/arts',
              'lifestyle': 'caetgory/lifestyle',
              'news': 'category/news',
              'panel': 'category/panel',
              'sport': 'category/sport',
              'abc1': 'channel/abc1',
              'abc2': 'channel/abc2',
              'abc3': 'channel/abc3',
              'news24': 'channel/news24',
              'iview': 'channel/iview',
              'trailers': 'channel/abc1',
              'featured': 'channel/abc1',
              'recent': 'channel/abc1',
              'last-chance': 'channel/abc1'}

TZ_LIST = {'Australia/ACT': [10, 0, 11, 0],
           'Australia/Adelaide': [9, 30, 10, 30],
           'Australia/Brisbane': [10, 0, 10, 0],
           'Australia/Broken_Hill': [9, 30, 10, 30],
           'Australia/Canberra': [10, 0, 11, 0],
           'Australia/Currie': [10, 0, 11, 0],
           'Australia/Darwin': [9, 30, 9, 30],
           'Australia/Eucla': [8, 45, 8, 45],
           'Australia/Hobart': [10, 0, 11, 0],
           'Australia/LHI': [10, 30, 11, 0],
           'Australia/Lindeman': [10, 0, 10, 0],
           'Australia/Lord_Howe': [10, 30, 11, 0],
           'Australia/Melbourne': [10, 0, 11, 0],
           'Australia/North': [9, 30, 9, 30],
           'Australia/NSW': [10, 0, 11, 0],
           'Australia/Perth': [8, 0, 8, 0],
           'Australia/Queensland': [10, 0, 10, 0],
           'Australia/South': [9, 30, 10, 30],
           'Australia/Sydney': [10, 0, 11, 0],
           'Australia/Tasmania': [10, 0, 11, 0],
           'Australia/Victoria': [10, 0, 11, 0],
           'Australia/West': [8, 0, 8, 0],
           'Australia/Yancowinna': [9, 30, 10, 30]}
