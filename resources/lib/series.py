import sys

import comm

from aussieaddonscommon import utils

import xbmcgui

import xbmcplugin


def make_series_list(params):

    try:
        category = params["category"]
        series_list = comm.get_programme_from_feed(category)
        series_list.sort()

        ok = True
        for s in series_list:
            url = "{0}?action=series_list&{1}".format(sys.argv[0],
                                                      s.make_kodi_url())
            thumb = s.get_thumb()
            listitem = xbmcgui.ListItem(s.get_list_title(),
                                        iconImage=thumb,
                                        thumbnailImage=thumb)
            listitem.setInfo('video', {'plot': s.get_description()})
            if s.type == 'Program':
                listitem.setProperty('IsPlayable', 'true')
                folder = False
            else:
                folder = True

            # add the item to the media list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=folder)
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
    except Exception as e:
        utils.handle_error('Unable to fetch program list. '
                           'Please try again later.')
        raise e
