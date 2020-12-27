import sys

from aussieaddonscommon import utils

import resources.lib.comm as comm

import xbmcgui

import xbmcplugin


def make_series_list(params, atoz=True):

    try:
        if atoz:
            series_list = comm.get_atoz_programme_from_feed(params)
        else:
            series_list = comm.get_collection_from_feed(params)
        series_list.sort()
        ok = True
        for s in series_list:
            thumb = s.get_thumb()
            listitem = xbmcgui.ListItem(s.get_list_title())
            listitem.setArt({'fanart': s.get_fanart(),
                             'icon': thumb,
                             'thumb': thumb})
            listitem.setInfo('video', {'plot': s.get_description()})
            if s.type == 'Program':
                listitem.setProperty('IsPlayable', 'true')
                folder = False
                url = "{0}?action=program_list{1}".format(
                    sys.argv[0], s.make_kodi_url())
            else:
                folder = True
                url = "{0}?action=series_list&{1}".format(
                    sys.argv[0], s.make_kodi_url())

            # add the item to the media list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=folder)
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
    except Exception:
        utils.handle_error('Unable to fetch program list. '
                           'Please try again later.')
