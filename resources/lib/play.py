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

import classes
import comm
import os
import parse
import sys
import urllib2
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

from aussieaddonscommon import utils

from pycaption import SRTWriter
from pycaption import WebVTTReader


def play(url):
    try:
        # Remove cookies.dat for Kodi < 17.0 - causes issues with playback
        addon = xbmcaddon.Addon()
        cookies_dat = xbmc.translatePath('special://home/cache/cookies.dat')
        if os.path.isfile(cookies_dat):
            os.remove(cookies_dat)
        p = classes.Program()
        p.parse_xbmc_url(url)
        stream = comm.get_stream_url(p.get_house_number(), p.get_url())
        use_ia = addon.getSetting('use_ia') == 'true'
        if use_ia:
            if addon.getSetting('ignore_drm') == 'false':
                try:
                    import drmhelper
                    if not drmhelper.check_inputstream(drm=False):
                        return
                except ImportError:
                    utils.log("Failed to import drmhelper")
                    utils.dialog_message(
                        'DRM Helper is needed for inputstream.adaptive '
                        'playback. Disable "Use inputstream.adaptive for '
                        'playback" in settings or install drmhelper. For '
                        'more information, please visit: '
                        'http://aussieaddons.com/drm')
                    return
            hdrs = stream[stream.find('|') + 1:]

        listitem = xbmcgui.ListItem(label=p.get_list_title(),
                                    iconImage=p.thumbnail,
                                    thumbnailImage=p.thumbnail,
                                    path=stream)
        if use_ia:
            listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
            listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
            listitem.setProperty('inputstream.adaptive.stream_headers', hdrs)
            listitem.setProperty('inputstream.adaptive.license_key', stream)
        listitem.setInfo('video', p.get_kodi_list_item())

        # Add subtitles if available
        if p.subtitle_url:
            profile = xbmcaddon.Addon().getAddonInfo('profile')
            path = xbmc.translatePath(profile).decode('utf-8')
            if not os.path.isdir(path):
                os.makedirs(path)
            subfile = xbmc.translatePath(
                os.path.join(path, 'subtitles.eng.srt'))
            if os.path.isfile(subfile):
                os.remove(subfile)

            try:
                webvtt_data = urllib2.urlopen(
                    p.subtitle_url).read().decode('utf-8')
                if webvtt_data:
                    with open(subfile, 'w') as f:
                        webvtt_subtitle = WebVTTReader().read(webvtt_data)
                        srt_subtitle = SRTWriter().write(webvtt_subtitle)
                        srt_unicode = srt_subtitle.encode('utf-8')
                        f.write(srt_unicode)
                if hasattr(listitem, 'setSubtitles'):
                    listitem.setSubtitles([subfile])
            except Exception as e:
                utils.log(
                    'Subtitles not available for this program {0}'.format(e))

        if hasattr(listitem, 'addStreamInfo'):
            listitem.addStreamInfo('audio', p.get_kodi_audio_stream_info())
            listitem.addStreamInfo('video', p.get_kodi_video_stream_info())

        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=listitem)

    except Exception:
        utils.handle_error('Unable to play video')
