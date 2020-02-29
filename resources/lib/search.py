import json
import sys

from future.moves.urllib.parse import quote_plus

from aussieaddonscommon import utils

import resources.lib.comm as comm

import xbmc

import xbmcaddon

import xbmcgui

import xbmcplugin


def get_search_history():
    addon = xbmcaddon.Addon()
    search_history = addon.getSetting('SEARCH_HISTORY')
    if search_history == '':
        addon.setSetting('SEARCH_HISTORY', json.dumps([]))
        return []
    json_data = json.loads(search_history)
    return json_data


def get_search_input():
    search_string = xbmcgui.Dialog().input('Enter search terms')
    if not search_string:
        return
    add_to_search_history(search_string)
    make_search_list({'name': search_string})


def set_search_history(json_data):
    addon = xbmcaddon.Addon()
    addon.setSetting('SEARCH_HISTORY', json.dumps(json_data))


def get_search_history_listing():
    listing = ['New Search']
    search_history = get_search_history()
    for item in search_history:
        listing.append(item)
    return listing


def add_to_search_history(search_string):
    search_history = get_search_history()
    if search_string not in search_history:
        search_history.append(search_string)
        set_search_history(search_history)


def remove_from_search_history(search_string):
    search_history = get_search_history()
    if search_string in search_history:
        search_history.remove(search_string)
        set_search_history(search_history)
    xbmc.executebuiltin('Container.Refresh')


def make_search_history_list():
    try:
        listing = get_search_history_listing()
        ok = True
        for item in listing:
            listitem = xbmcgui.ListItem(label=item)
            listitem.setInfo('video', {'plot': ''})
            listitem.addContextMenuItems(
                [('Remove from search history',
                  ('RunPlugin(plugin://plugin.video.abc_iview/?action=remove'
                   'search&name={0})'.format(item)))])
            url = "{0}?action=searchhistory&name={1}".format(
                sys.argv[0], quote_plus(item))

            # Add the program item to the list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=True)
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok,
                                  cacheToDisc=False)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
    except Exception as e:
        utils.handle_error('Unable to fetch search history list')
        raise e


def make_search_list(params):
    try:
        listing = comm.get_search_results(params.get('name'))
        ok = True
        for s in listing:
            url = "{0}?action=series_list&{1}".format(sys.argv[0],
                                                      s.make_kodi_url())
            thumb = s.get_thumb()
            listitem = xbmcgui.ListItem(s.get_list_title())
            listitem.setArt({'icon': thumb,
                             'thumb': thumb})
            listitem.setInfo('video', {'plot': s.get_description()})
            folder = False
            if s.type == 'Program':
                listitem.setProperty('IsPlayable', 'true')
            else:
                if not s.dummy:
                    folder = True

            # add the item to the media list
            ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),
                                             url=url,
                                             listitem=listitem,
                                             isFolder=folder)
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=ok)
        xbmcplugin.setContent(handle=int(sys.argv[1]), content='tvshows')
    except Exception:
        utils.handle_error('Unable to fetch search history list')
