import sys

import comm

from aussieaddonscommon import utils

import xbmcgui

import xbmcplugin


def make_programs_list(params):
    try:
        programs = comm.get_series_from_feed(params['url'])

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
            url = "{0}?action=program_list&{1}".format(sys.argv[0],
                                                       p.make_kodi_url())

            # Add the program item to the list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=False,
                                             totalItems=len(programs))

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except Exception as e:
        utils.handle_error('Unable to fetch program list')
        raise e
