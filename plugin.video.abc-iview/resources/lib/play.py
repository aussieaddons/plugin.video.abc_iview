#
#	ABC iView XBMC Plugin
#	Copyright (C) 2012 Andy Botting
#
#  This plugin includes from from python-iview
#  Copyright (C) 2009-2012 by Jeremy Visser <jeremy@visser.name>
#
#	This plugin is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This plugin is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this plugin. If not, see <http://www.gnu.org/licenses/>.
#

import sys
import config
import utils
import classes
import comm

try:
	import xbmc, xbmcgui, xbmcplugin
except ImportError:
	pass # for PC debugging

def play(url):

	try:
		iview_config = comm.get_config()
		auth = comm.get_auth(iview_config)

		# We don't support Adobe HDS yet, Fallback to RTMP streaming server
		if auth['rtmp_url'].startswith('http://'):
			auth['rtmp_url'] = iview_config['rtmp_url'] or config.akamai_fallback_server
			auth['playpath_prefix'] = config.akamai_playpath_prefix
			utils.log("Adobe HDS Not Supported, using fallback server %s" % auth['rtmp_url'])

		p = classes.Program()
		p.parse_xbmc_url(url)

		# Playpath shoud look like this:
		# 	Akamai: mp4:flash/playback/_definst_/itcrowd_10_03_02
		playpath = auth['playpath_prefix'] + p.url
		if playpath.split('.')[-1] == 'mp4':
			playpath = 'mp4:' + playpath
	
		# Strip off the .flv or .mp4
		playpath = playpath.split('.')[0]
	
		# rtmp://cp53909.edgefcs.net/ondemand?auth=daEbjbeaCbGcgb6bedYacdWcsdXc7cWbDda-bmt0Pk-8-slp_zFtpL&aifp=v001 
		# playpath=mp4:flash/playback/_definst_/kids/astroboy_10_01_22 swfurl=http://www.abc.net.au/iview/images/iview.jpg swfvfy=true
		rtmp_url = "%s?auth=%s playpath=%s swfurl=%s swfvfy=true" % (auth['rtmp_url'], auth['token'], playpath, config.swf_url)
	
		listitem=xbmcgui.ListItem(label=p.get_list_title(), iconImage=p.thumbnail, thumbnailImage=p.thumbnail)
		listitem.setInfo('video', p.get_xbmc_list_item())
		listitem.addStreamInfo('video', p.get_xbmc_stream_info())
	
		xbmc.Player().play(rtmp_url, listitem)
	except:
		# oops print error message
		d = xbmcgui.Dialog()
		message = utils.dialog_error("Unable to play video")
		d.ok(*message)
		utils.log_error();

