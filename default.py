import sys

from aussieaddonscommon import utils
print utils

from resources.lib import categories
from resources.lib import collect
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

    addon = xbmcaddon.Addon()
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
                addon.openSettings()
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
        elif action == 'open_ia_settings':
            try:
                import drmhelper
                if drmhelper.check_inputstream(drm=False):
                    ia = drmhelper.get_addon()
                    ia.openSettings()
                else:
                    utils.dialog_message(
                        "Can't open inputstream.adaptive settings")
            except Exception:
                utils.dialog_message(
                    "Can't open inputstream.adaptive settings")


if __name__ == '__main__':
    main()
