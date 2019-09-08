import sys

import comm

from future.moves.urllib.parse import quote_plus

from aussieaddonscommon import utils

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
            url = '{0}?action=category_list&category={1}'.format(
                sys.argv[0], quote_plus(c['path']))
            listitem = xbmcgui.ListItem(c['name'])
            if 'thumb' in c:
                listitem.setArt({'thumb': c['thumb']})

            # Add the program item to the list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=True)

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except Exception as e:
        utils.handle_error('Unable to build category list')
        raise e
