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


def get_categories():
	iview_config = comm.get_config()
	categories = comm.get_categories(iview_config)
	return categories


def make_category_list():
	try:
		category_list = get_categories()
		category_list = sorted(category_list, key=lambda k: k['name'].lower())
		category_list.insert(0, {'name':'All', 'keyword':'0-z'})

		# fill media list
		ok = fill_category_list(category_list)
	except:
		d = xbmcgui.Dialog()
		message = utils.dialog_error("Unable to fetch listing")
		d.ok(*message)
		utils.log_error();
		ok = False

	# send notification we're finished, successfully or unsuccessfully
	xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)



def fill_category_list(category_list):
	iview_config = comm.get_config()
	try:
		ok = True
		# enumerate through the list of categories and add the item to the media list
		for g in category_list:
			url = "%s?category_id=%s" % (sys.argv[0], g['keyword'])
			listitem = xbmcgui.ListItem(g['name'])

			# add the item to the media list
			ok = xbmcplugin.addDirectoryItem(
				handle=int(sys.argv[1]),
				url=url,
				listitem=listitem,
				isFolder=True,
				totalItems=len(category_list)
			)

			# if user cancels, call raise to exit loop
			if (not ok):
				raise

	except:
		# user cancelled dialog or an error occurred
		utils.log_error()
		ok = False
	return ok

