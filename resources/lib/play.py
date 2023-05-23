import io
import os
import sys

from aussieaddonscommon import session
from aussieaddonscommon import utils
from aussieaddonscommon.exceptions import AussieAddonsException

from future.moves.urllib.parse import quote_plus

from pycaption import SRTWriter
from pycaption import WebVTTReader

import resources.lib.comm as comm

import xbmcaddon

import xbmcgui

import xbmcplugin

try:
    from xbmc import translatePath
except ImportError:
    from xbmcvfs import translatePath


def play(params):
    try:
        # Remove cookies.dat for Kodi < 17.0 - causes issues with playback
        addon = xbmcaddon.Addon()
        if utils.get_kodi_major_version() < 17:
            cookies_dat = translatePath(
                'special://home/cache/cookies.dat')
            if os.path.isfile(cookies_dat):
                os.remove(cookies_dat)
        p = comm.get_stream_program(params)
        port = addon.getSetting('playlist_port')
        stream_url = p.get_stream_url()
        if not stream_url:
            utils.log('Not Playable: {0}'.format(repr(stream_url)))
            failure_data = p.get_failure_msg()
            raise AussieAddonsException(
                'Not available: {0}\n{1}'.format(failure_data.get('msg'),
                                                 failure_data.get(
                                                     'availability')))
        playlist_has_error = comm.check_playlist(p)
        if playlist_has_error:
            utils.log('Playlist has erroneous audio attributes, fixing via proxy...')
            stream_url = "http://127.0.0.1:{0}/{1}".format(port, quote_plus(p.get_stream_url()))
        else:
            utils.log('Playlist check returns good...')

        use_ia = addon.getSetting('USE_IA') == 'true'
        if use_ia:
            if addon.getSetting('IGNORE_DRM') == 'false':
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
            hdrs = p.headers_string

        listitem = xbmcgui.ListItem(label=p.get_list_title(),
                                    path=stream_url)
        thumb = p.get_thumb()
        listitem.setArt({'icon': thumb,
                         'thumb': thumb})
        if use_ia:
            if utils.get_kodi_major_version() < 19:
                listitem.setProperty('inputstreamaddon', 'inputstream.adaptive')
            else:
                listitem.setProperty('inputstream', 'inputstream.adaptive')
            #auth_hdrs = comm.get_drm_auth(p)
            listitem.setProperty('inputstream.adaptive.manifest_type', 'hls')
            listitem.setProperty('inputstream.adaptive.stream_headers', hdrs)
            listitem.setProperty('inputstream.adaptive.manifest_headers', hdrs)
            listitem.setProperty('inputstream.adaptive.license_key',
                                 p.get_stream_url())
            #listitem.setProperty('inputstream.adaptive.license_type', 'com.widevine.alpha')
            #key = 'https://wv-keyos.licensekeyserver.com/|customdata={cd}|R{SSM}|B'.format(cd=auth_hdrs, SSM='{SSM}')
            #listitem.setProperty('inputstream.adaptive.license_key', key)
        listitem.setInfo('video', p.get_kodi_list_item())

        # Add subtitles if available

        if p.is_captions():
            profile = xbmcaddon.Addon().getAddonInfo('profile')
            path = translatePath(profile)
            if not os.path.isdir(path):
                os.makedirs(path)
            caption_file = os.path.join(path, 'subtitles.eng.srt')
            if os.path.isfile(caption_file):
                try:
                    os.remove(caption_file)
                except WindowsError as e:
                    utils.log('Subtitles not available for this '
                              'program: {0}'.format(e))

            try:
                sess = session.Session()
                webvtt_data = sess.get(p.get_captions_url()).text
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

        if hasattr(listitem, 'addStreamInfo'):
            listitem.addStreamInfo('audio', p.get_kodi_audio_stream_info())
            listitem.addStreamInfo('video', p.get_kodi_video_stream_info())

        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=listitem)

    except Exception:
        utils.handle_error('Unable to play video')
