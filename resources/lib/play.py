import io
import os
import sys

from aussieaddonscommon import session
from aussieaddonscommon import utils
from aussieaddonscommon.exceptions import AussieAddonsException

from pycaption import SRTWriter
from pycaption import WebVTTReader

import resources.lib.classes as classes
import resources.lib.comm as comm

import xbmc

import xbmcaddon

import xbmcgui

import xbmcplugin


def play(url):
    try:
        # Remove cookies.dat for Kodi < 17.0 - causes issues with playback
        addon = xbmcaddon.Addon()
        cookies_dat = xbmc.translatePath('special://home/cache/cookies.dat')
        if os.path.isfile(cookies_dat):
            os.remove(cookies_dat)
        p = classes.Program()
        p.parse_kodi_url(url)
        stream_data = comm.get_stream_url(p.get_house_number(), p.get_url())
        stream_url = stream_data.get('stream_url')
        if not stream_url:
            utils.log('Not Playable: {0}'.format(repr(stream_data)))
            raise AussieAddonsException(
                'Not available: {0}\n{1}'.format(stream_data.get('msg'),
                                                 stream_data.get(
                                                     'availability')))
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
            hdrs = stream_url[stream_url.find('|') + 1:]

        listitem = xbmcgui.ListItem(label=p.get_list_title(),
                                    iconImage=p.thumb,
                                    thumbnailImage=p.thumb,
                                    path=stream_url)
        if use_ia:
            listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
            listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
            listitem.setProperty('inputstream.adaptive.stream_headers', hdrs)
            listitem.setProperty('inputstream.adaptive.license_key',
                                 stream_url)
        listitem.setInfo('video', p.get_kodi_list_item())

        # Add subtitles if available

        if p.is_captions():
            captions_url = stream_data.get('captions_url')
            profile = xbmcaddon.Addon().getAddonInfo('profile')
            path = xbmc.translatePath(profile)
            if not os.path.isdir(path):
                os.makedirs(path)
            caption_file = os.path.join(path, 'subtitles.eng.srt')
            if os.path.isfile(caption_file):
                os.remove(caption_file)

            try:
                sess = session.Session()
                webvtt_data = sess.get(captions_url).text
                if webvtt_data:
                    with io.BytesIO() as buf:
                        webvtt_captions = WebVTTReader().read(webvtt_data)
                        srt_captions = SRTWriter().write(webvtt_captions)
                        srt_unicode = srt_captions.encode('utf-8')
                        buf.write(srt_unicode)
                        with io.open(caption_file, "wb") as f:
                            f.write(buf.getvalue())
                if hasattr(listitem, 'setSubtitles'):
                    listitem.setSubtitles([caption_file])
            except Exception as e:
                utils.log(
                    'Subtitles not available for this program: {0}'.format(e))
                raise

        if hasattr(listitem, 'addStreamInfo'):
            listitem.addStreamInfo('audio', p.get_kodi_audio_stream_info())
            listitem.addStreamInfo('video', p.get_kodi_video_stream_info())

        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=listitem)

    except Exception as e:
        utils.handle_error('Unable to play video')
        raise e
