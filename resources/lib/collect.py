from __future__ import unicode_literals

import sys

from aussieaddonscommon import utils

import resources.lib.comm as comm

import xbmcgui

import xbmcplugin


def make_collect_list(params):

    try:
        collect_list = comm.get_collections_from_feed(params)
        collect_list.sort()
        ok = True
        for c in collect_list:
            url = str('{0}?action=collect_list&{1}'.format(
                sys.argv[0], c.make_kodi_url()))
            listitem = xbmcgui.ListItem(c.get_title())
            listitem.setInfo('video', {})
            listitem.setArt({'fanart': c.get_fanart()})
            folder = True
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=folder)
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
    except Exception:
        utils.handle_error('Unable to fetch program list. '
                           'Please try again later.')
