import sys

from aussieaddonscommon import utils

from resources.lib import categories
from resources.lib import live
from resources.lib import play
from resources.lib import programs
from resources.lib import search
from resources.lib import series

import xbmcaddon

import xbmcgui

# Print our platform/version debugging information
utils.log_kodi_platform_version()


def main():
    params_str = sys.argv[2]
    params = utils.get_url(params_str)

    if (len(params) == 0):
        categories.make_category_list()

    elif 'action' in params:
        action = params.get('action')

        if action in ['program_list', 'livestreams']:
            play.play(params_str)
        elif action == 'series_list':
            if params.get('type') == 'Series':
                programs.make_programs_list(params)
            else:
                play.play(params_str)
        elif action == 'category_list':
            category = params.get('category')
            if category == 'settings':
                xbmcaddon.Addon().openSettings()
            elif category == 'livestreams':
                live.make_livestreams_list()
            elif category == 'search':
                search.make_search_history_list()
            else:
                series.make_series_list(params)
        elif action == 'searchhistory':
            if params.get('name') == 'New Search':
                search.get_search_input()
            else:
                search.make_search_list(params)
        elif action == 'removesearch':
            search.remove_from_search_history(params.get('name'))
        elif action == 'sendreport':
            utils.user_report()
        elif action == 'update_ia':
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


if __name__ == '__main__':
    main()
