import sys

from aussieaddonscommon import utils

import resources.lib.comm as comm

import xbmcgui

import xbmcplugin


def make_livestreams_list():
    try:
        programs = comm.get_livestreams_from_feed()

        ok = True
        for p in programs:
            listitem = xbmcgui.ListItem(label=p.get_list_title(),
                                        iconImage=p.get_thumb(),
                                        thumbnailImage=p.get_thumb())
            listitem.setInfo('video', p.get_kodi_list_item())
            listitem.setProperty('IsPlayable', 'true')

            if p.get_fanart():
                listitem.setArt({'fanart': p.get_fanart()})

            if hasattr(listitem, 'addStreamInfo'):
                listitem.addStreamInfo('audio', p.get_kodi_audio_stream_info())
                listitem.addStreamInfo('video', p.get_kodi_video_stream_info())

            # Build the URL for the program, including the list_info
            url = "{0}?action=livestreams&{1}".format(sys.argv[0],
                                                      p.make_kodi_url())

            # Add the program item to the list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=False,
                                             totalItems=len(programs))

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except Exception:
        utils.handle_error('Unable to fetch livestream list')
