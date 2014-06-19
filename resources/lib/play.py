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
import classes, comm, config, utils
import xbmc, xbmcgui, xbmcplugin, xbmcaddon

def http_url(p):
    # Work out new series ID
    program_data = comm.get_new_programme(p.id)
    feed_data = comm.get_program_from_feed(program_data['episodeHouseNumber'], program_data['seriesHouseNumber'])
    return feed_data['videoasset']

def rtmp_url(p):
    iview_config = comm.get_config()
    auth = comm.get_auth(iview_config)

    # We don't support Adobe HDS yet, Fallback to RTMP streaming server
    if auth['rtmp_url'].startswith('http://'):
        auth['rtmp_url'] = iview_config['rtmp_url'] or config.akamai_fallback_server
        auth['playpath_prefix'] = config.akamai_playpath_prefix
        utils.log("Adobe HDS Not Supported, using fallback server %s" % auth['rtmp_url'])

    # Playpath shoud look like this:
    #   Akamai: mp4:flash/playback/_definst_/itcrowd_10_03_02
    playpath = auth['playpath_prefix'] + p.url
    if playpath.split('.')[-1] == 'mp4':
        playpath = 'mp4:' + playpath

    # Strip off the .flv or .mp4
    playpath = playpath.split('.')[0]

    # rtmp://cp53909.edgefcs.net/ondemand?auth=daEbjbeaCbGcgb6bedYacdWcsdXc7cWbDda-bmt0Pk-8-slp_zFtpL&aifp=v001 
    # playpath=mp4:flash/playback/_definst_/kids/astroboy_10_01_22 swfurl=http://www.abc.net.au/iview/images/iview.jpg swfvfy=true
    return "%s?auth=%s playpath=%s swfurl=%s swfvfy=true" % (auth['rtmp_url'], auth['token'], playpath, config.swf_url)

def play(url):
    addon = xbmcaddon.Addon(config.ADDON_ID)

    try:
        p = classes.Program()
        p.parse_xbmc_url(url)

        if addon and addon.getSetting('video_transport') == 'RTMP':
            utils.log('Using RTMP Transport')
            media_url = rtmp_url(p)
        else:
            utils.log('Using HTTP Transport')
            media_url = http_url(p)
    
        listitem=xbmcgui.ListItem(label=p.get_list_title(), iconImage=p.thumbnail, thumbnailImage=p.thumbnail)
        listitem.setInfo('video', p.get_xbmc_list_item())

        if hasattr(listitem, 'addStreamInfo'):
            listitem.addStreamInfo('audio', p.get_xbmc_audio_stream_info())
            listitem.addStreamInfo('video', p.get_xbmc_video_stream_info())
    
        xbmc.Player().play(media_url, listitem)
    except:
        utils.handle_error("Unable to play video")
