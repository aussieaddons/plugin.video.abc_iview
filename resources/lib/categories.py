import sys

from future.moves.urllib.parse import quote_plus

from aussieaddonscommon import utils

import resources.lib.comm as comm

import xbmcgui

import xbmcplugin


def make_category_list():
    try:
        categories = comm.get_categories()
        categories.append({'path': 'livestreams', 'name': 'Live Streams'})
        categories.append({'path': 'search', 'name': 'Search'})
        categories.append({'path': 'settings', 'name': 'Settings'})

        ok = True
        for c in categories:
            thumb = c.get('thumb')
            url = '{0}?action=category_list&category={1}'.format(
                sys.argv[0], quote_plus(c['path']))
            listitem = xbmcgui.ListItem(c['name'])

            if thumb:
                listitem.setArt({'thumb': thumb,
                                 'icon': thumb})
                url += '&fanart={0}'.format(thumb)

            # Add the program item to the list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=True)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
    except Exception:
        utils.handle_error('Unable to build category list')
