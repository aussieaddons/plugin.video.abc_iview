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
import os
import urllib2
import urllib
import comm
import utils

try:
	import xbmc, xbmcgui, xbmcplugin
except ImportError:
	pass # for PC debugging

BASE_SKIN_THUMBNAIL_PATH = os.path.join(os.getcwd(), 'resources', 'media')
BASE_PLUGIN_THUMBNAIL_PATH = os.path.join(os.getcwd(), 'resources', 'media')


def get_series():
	iview_config = comm.get_config()
	programme = comm.get_programme(iview_config)
	return programme


def make_series_list():
	try:
		series_list = get_series()
		series_list.sort()

		# fill media list
		ok = fill_series_list(series_list)
	except:
		d = xbmcgui.Dialog()
		message = utils.dialog_error("Unable to fetch listing")
		d.ok(*message)
		utils.log_error();
		ok = False

	# send notification we're finished, successfully or unsuccessfully
	xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)



def fill_series_list(series_list):
	iview_config = comm.get_config()
	try:
		ok = True
		# enumerate through the list of categories and add the item to the media list
		for s in series_list:
			url = "%s?series_id=%s" % (sys.argv[0], s.id)
			#thumbnail = get_thumbnail(s.id)
			thumbnail = ''

			listitem = xbmcgui.ListItem(s.get_list_title(), thumbnailImage=thumbnail)

			# add the item to the media list
			ok = xbmcplugin.addDirectoryItem(
				handle=int(sys.argv[1]), 
				url=url, 
				listitem=listitem, 
				isFolder=True, 
				totalItems=len(series_list)
			)

			# if user cancels, call raise to exit loop
			if (not ok): 
				raise

		xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
	except:
		# user cancelled dialog or an error occurred
		utils.log_error()
		ok = False
	return ok

