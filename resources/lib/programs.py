import sys

from aussieaddonscommon import utils

import resources.lib.comm as comm

import xbmcgui

import xbmcplugin


def make_programs_list(params):
    try:
        from_series_list = params.get('from_serieslist') == 'True'
        programs = comm.get_series_from_feed(params['url'], from_series_list)

        ok = True
        for p in programs:
            listitem = xbmcgui.ListItem(label=p.get_list_title(),
                                        iconImage=p.get_thumb(),
                                        thumbnailImage=p.get_thumb())

            if p.type == 'Program':
                listitem.setInfo('video', p.get_kodi_list_item())
                listitem.setProperty('IsPlayable', 'true')
                if hasattr(listitem, 'addStreamInfo'):
                    listitem.addStreamInfo('audio',
                                           p.get_kodi_audio_stream_info())
                    listitem.addStreamInfo('video',
                                           p.get_kodi_video_stream_info())
                fanart = p.get_fanart()
                folder = False
                url = "{0}?action=program_list&{1}".format(sys.argv[0],
                                                           p.make_kodi_url())
            else:
                fanart = params.get('fanart')
                folder = True
                url = "{0}?action=series_list&{1}".format(sys.argv[0],
                                                          p.make_kodi_url())

            listitem.setArt({'fanart': fanart})

            # Add the program item to the list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=folder,
                                             totalItems=len(programs))

        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
    except Exception:
        utils.handle_error('Unable to fetch program list')
