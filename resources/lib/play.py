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

import sys
import os
import urllib
import urllib2
import json
import classes
import comm
import config
import parse
import utils
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

def play(url):

    try:
        p = classes.Program()
        p.parse_xbmc_url(url)
        auth = utils.get_auth(p)
        akamai_auth = utils.get_akamai_auth(auth)
        akamai_url = "{0}?hdnea={1}".format(p.get_url(), akamai_auth)
        streams_list = comm.fetch_url_withcookies(akamai_url)
        quality = xbmcaddon.Addon().getSetting('HLSQUALITY')
        stream_url = parse.parse_m3u8_streams(streams_list, quality)
        cookies = utils.cookies_to_string(comm.cj)
        url_to_play = '{0}|{1}={2}&Cookie={3}'.format(stream_url, 
                        config.user_agent[0][0], 
                        urllib.quote(config.user_agent[0][1]), 
                        urllib.quote(cookies))
        
        listitem=xbmcgui.ListItem(label=p.get_list_title(),
                                  iconImage=p.thumbnail,
                                  thumbnailImage=p.thumbnail,
                                  path=url_to_play)

        listitem.setInfo('video', p.get_xbmc_list_item())

        #add subtitles if available
        addon = xbmcaddon.Addon(config.ADDON_ID)
        subtitles = None
        if addon.getSetting('subtitles_enabled') == 'true':
            profile = xbmcaddon.Addon().getAddonInfo('profile')
            path = xbmc.translatePath(profile).decode('utf-8')
            if not os.path.isdir(path):
                os.makedirs(path)
            subfile = xbmc.translatePath(os.path.join(path, 'subtitles.eng.srt'))
            if os.path.isfile(subfile):
                os.remove(subfile)
            
            try:
                data = urllib2.urlopen(p.subtitle_url).read()
                f = open(subfile, 'w')
                f.write(parse.convert_to_srt(data))
                f.close()
                if hasattr(listitem, 'setSubtitles'):
                    # This function only supported from Kodi v14+
                    listitem.setSubtitles([subfile])
                else:
                    subtitles = True
            except:
                utils.log('Subtitles not available for this program')

        if hasattr(listitem, 'addStreamInfo'):
            listitem.addStreamInfo('audio', p.get_xbmc_audio_stream_info())
            listitem.addStreamInfo('video', p.get_xbmc_video_stream_info())

        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem=listitem)

        # Enable subtitles for XBMC v13
        if addon.getSetting('subtitles_enabled') == "true":
            if subtitles == True:
                if not hasattr(listitem, 'setSubtitles'):
                    player = xbmc.Player()
                    while not player.isPlaying():
                        xbmc.sleep(100) # wait until video is being played
                        player.setSubtitles(subfile)

    except:
        utils.handle_error("Unable to play video")
