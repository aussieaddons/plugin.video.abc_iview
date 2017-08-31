#
#  ABC iView XBMC Addon
#  Copyright (C) 2012 Andy Botting
#
#  This plugin includes code from python-iview
#  Copyright (C) 2009-2012 by Jeremy Visser <jeremy@visser.name>
#
#  This plugin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This plugin is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this plugin. If not, see <http://www.gnu.org/licenses/>.
#

import os
import sys
import xbmcaddon
import xbmcgui

from aussieaddonscommon import utils

# Add our resources/lib to the python path
addon_dir = xbmcaddon.Addon().getAddonInfo('path')
sys.path.insert(0, os.path.join(addon_dir, 'resources', 'lib'))

import categories  # noqa: E402
import play  # noqa: E402
import programs  # noqa: E402
import series  # noqa: E402

# Print our platform/version debugging information
utils.log_kodi_platform_version()

if __name__ == '__main__':
    params_str = sys.argv[2]
    params = utils.get_url(params_str)

    if (len(params) == 0):
        categories.make_category_list()
    elif 'series' in params:
        xbmcgui.Dialog().ok(
            'Outdated Favourites Link',
            'The Kodi Favourite item being accessed was created with an '
            'earlier version of the iView add-on and is no longer '
            'compatible. Please remove this link and update with a new '
            'one')
    elif 'play' in params:
        play.play(params_str)
    elif 'series_url' in params:
        programs.make_programs_list(params_str)
    elif 'category' in params:
        if params['category'] == 'settings':
            xbmcaddon.Addon().openSettings()
        else:
            series.make_series_list(params_str)
    elif 'action' in params:
        if params['action'] == 'sendreport':
            utils.user_report()
        elif params['action'] == 'update_ia':
            try:
                import drmhelper
                addon = drmhelper.get_addon(drm=False)
                if not drmhelper.is_ia_current(addon, latest=True):
                    if xbmcgui.Dialog().yesno(
                        'Upgrade?', ('Newer version of inputstream.adaptive '
                                     'available ({0}) - would you like to '
                                     'upgrade to this version?'.format(
                                        drmhelper.get_latest_ia_ver()))):
                        drmhelper.get_ia_direct(update=True, drm=False)
                else:
                    ver = addon.getAddonInfo('version')
                    utils.dialog_message('Up to date: Inputstream.adaptive '
                                         'version {0} installed and enabled.'
                                         ''.format(ver))
            except ImportError:
                utils.log("Failed to import drmhelper")
                utils.dialog_message('DRM Helper is needed for this function. '
                                     'For more information, please visit: '
                                     'http://aussieaddons.com/drm')
