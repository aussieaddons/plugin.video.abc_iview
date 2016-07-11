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

import sys
import os
import urllib2
import urllib
import comm
import utils
import xbmcgui
import xbmcplugin

def make_category_list():

    try:
        iview_config = comm.get_config()
        categories = comm.get_categories(iview_config)
        categories = sorted(categories, key=lambda k: k['name'].lower())
        # All category is disabled for now due to API issues
        # https://github.com/andybotting/xbmc-addon-abc-iview/issues/1454
        #categories.insert(0, {'name':'All', 'keyword':'0-z'})

        ok = True
        for g in categories:
            url = "%s?category=%s" % (sys.argv[0], g['keyword'])
            listitem = xbmcgui.ListItem(g['name'])

            # Add the program item to the list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=True)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except:
        utils.handle_error()
