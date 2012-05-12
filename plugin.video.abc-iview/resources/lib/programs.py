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
import comm

try:
	import xbmc, xbmcgui, xbmcplugin
except ImportError:
	pass # for PC debugging


def get_programs(series_id):
	iview_config = comm.get_config()
	return comm.get_series_items(iview_config, series_id)


def make_programs_list(url):
	params = utils.get_url(url)	

	try:
		programs = get_programs(params["series_id"])
		# fill media list
		ok = fill_programs_list(programs)
	except:
		# oops print error message
		d = xbmcgui.Dialog()
		msg = utils.dialog_error("Unable to fetch listing")
		d.ok(*msg)
		utils.log_error();
		ok = False

	# send notification we're finished, successfully or unsuccessfully
	xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)


def fill_programs_list(programs):
	try:	
		ok = True
		for p in programs:

			item_info = p.get_xbmc_list_item()
			item_url = p.make_xbmc_url()

			listitem = xbmcgui.ListItem(label=p.get_list_title(), iconImage=p.get_thumbnail(), thumbnailImage=p.get_thumbnail())
			listitem.setInfo('video', item_info)

			# Build the URL for the program, including the list_info
			url = "%s?play=true&%s" % (sys.argv[0], item_url)

			# Add the program item to the list
			ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False, totalItems=len(programs))
			xbmcplugin.setContent(handle=int(sys.argv[1]), content='episodes')
	except:
		# user cancelled dialog or an error occurred
		d = xbmcgui.Dialog()
		title = "%s Error" % config.NAME
		msg = utils.dialog_error("Unable to fetch listing")
		d.ok(*msg)
		utils.log_error()
		ok = False
	return ok
