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

	iview_config = comm.get_config()
	auth = comm.get_auth(iview_config)

	p = classes.Program()
	p.parse_xbmc_url(url)

	try:
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
	
		xbmc.Player().play(rtmp_url, listitem)
	except:
		# oops print error message
		d = xbmcgui.Dialog()
		message = utils.dialog_error("Unable to play video")
		d.ok(*message)
		utils.log_error();

