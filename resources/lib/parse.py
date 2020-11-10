import json
import re

import resources.lib.classes as classes
import resources.lib.config as config


def parse_categories(config):
    """Fetch navigation json file and retrieve channels and categories."""
    categories_list = []
    data = json.loads(config)
    categories = []
    for x in data['items']:
        if x.get('id') in ['channels', 'categories']:
            for item in x.get('items'):
                categories.append(item)

    for cat in categories:
        item = {}
        item['path'] = cat['path']
        item['name'] = cat['title']
        if 'logoUrl' in cat:
            item['thumb'] = cat['logoUrl']
        categories_list.append(item)

    return categories_list


def parse_collections_from_feed(data, params):
    listing = []
    collection_json_data = json.loads(data)['_embedded'].get('collections')
    for collection in collection_json_data:
        if collection.get('title'):
            c = classes.Collect()
            c.title = collection.get('title')
            c.collection_id = collection.get('id')
            c.fanart = params.get('fanart')
            listing.append(c)
    return listing


def match_season_episode(subtitle):
    # Convoluted Season/Episode parsing
    if subtitle:
        # Series 2 Episode 25 Home Is Where The Hatch Is
        # Series 4 Ep:11 As A Yoga Yuppie
        # Series 4 Ep 10: Emission Impossible
        title_match = re.search(
            '^[Ss]eries\\s?(?P<series>\\w+):?\\s[Ee]p(isode)?:?\\s?('
            '?P<episode>\\d+):?\\s(?P<episode_title>.*)$',
            subtitle)  # noqa: E501
        if not title_match:
            # Series 8 Episode 13
            # Series 8 Episode:13
            title_match = re.search(
                '^[Ss]eries\\s?(?P<series>\\w+):?\\s?[Ee]p(isode)?:?\\s?('
                '?P<episode>\\d+)$',
                subtitle)  # noqa: E501
        if not title_match:
            # Episode 34 Shape Shifter
            # Ep:34 Shape Shifter
            title_match = re.search(
                '^[Ee]p(isode)?:?\\s?(?P<episode>\\d+):?\\s?('
                '?P<episode_title>.*)$',
                subtitle)  # noqa: E501
        if not title_match:
            # Series 10 Rylan Clark, Joanna Lumley, Ant And Dec
            title_match = re.search(
                '^[Ss]eries:?\\s?(?P<series>\\d+):?\\s(?P<episode_title>.*)$',
                subtitle)  # noqa: E501
        if not title_match:
            # Episode 5
            # Ep 5
            # Episode:5
            title_match = re.search('^[Ee]p(isode)?:?\\s?(?P<episode>\\d+)$',
                                    subtitle)  # noqa: E501
        return title_match


def set_episode_title_from_match(p, title_match, subtitle):
    title_parts = {}
    if not title_match:
        p.set_episode_title(subtitle)
    else:
        title_parts = title_match.groupdict()
        episode_title = title_parts.get('episode_title')
        if episode_title:
            p.set_episode_title(episode_title)
        else:  # episode is literally named 'Episode 1' etc.
            p.set_episode_title(subtitle)

    # If we only get series/episode in the subtitle
    p.set_season(title_parts.get('series'))
    p.set_episode(title_parts.get('episode'))


def parse_programme_from_feed(data, params):
    json_data = json.loads(data)
    show_list = []
    for show in json_data.get('items'):
        if show.get('_entity') == 'show':
            s = classes.Series()
            s.num_episodes = show.get('episodeCount')
            s.title = show.get('title')
            additional_title = ''
            if show.get('status'):
                additional_title = show['status'].get('title', '').lower()
            title_match = re.match(
                '^[Ss]eries\\s?(?P<series>\\w+)', additional_title)
            if title_match:
                s.title += ' Series ' + title_match.groups()[0]
            s.url = show.get('_links', '').get('deeplink', '').get(
                'href')
        elif show.get('_entity') == 'video':
            s = classes.Program()
            s.title = show.get('showTitle')
            subtitle = show.get('title')
            s.duration = show.get('duration')
            s.house_number = show.get('houseNumber')
            s.url = show.get('_links').get('self').get('href')
            title_match = match_season_episode(subtitle)
            set_episode_title_from_match(s, title_match, subtitle)
        else:
            continue
        s.description = show.get('title')
        s.thumb = show.get('thumbnail')
        fanart = params.get('fanart')
        if fanart:
            s.fanart = params.get('fanart')
        else:
            s.fanart = s.thumb
        show_list.append(s)
    return show_list


def parse_programs_from_feed(data, from_series_list=False):
    json_data = json.loads(data)
    programs_list = []
    serieslist_data = []

    fanart = json_data.get('thumbnail')
    if json_data.get('type') == 'series':
        item_list = json_data['_embedded']['selectedSeries'].get(
            '_embedded', {}).get('videoEpisodes')
        if not item_list:
            # Let's see if there are 'extras' instead.
            # Users may bookmark a series which will end up
            # empty, make sure we have an empty list to use instead
            item_list = json_data['_embedded']['selectedSeries'].get(
                '_embedded', {}).get('videoExtras', [])
        serieslist_data = json_data['_embedded']['seriesList']
    else:
        item_list = [json_data['_embedded']['highlightVideo']]

    for item in item_list:
        p = classes.Program()
        title = item.get('seriesTitle')
        if title:
            p.title = title
        else:
            p.title = item.get('title')

        title_match = match_season_episode(item.get('title'))
        set_episode_title_from_match(p, title_match, item.get('title'))
        p.house_number = item.get('houseNumber')
        p.description = item.get('description')
        p.thumb = item.get('thumbnail')
        p.fanart = fanart
        p.url = item['_links']['self'].get('href')
        p.rating = item.get('classification')
        p.duration = item.get('duration')
        p.captions = item.get('captions')
        p.set_date(item.get('pubDate'))
        p.set_expire(item.get('expireDate'))

        programs_list.append(p)

    sorted_programs = sorted(programs_list,
                             key=lambda x: x.get_date_time(),
                             reverse=True)
    if len(serieslist_data) > 1 and not from_series_list:
        for series in serieslist_data:
            if series.get('id') == json_data['_embedded'][
                    'selectedSeries'].get('id'):
                continue
            s = classes.Series()
            s.title = series.get('title')
            s.url = series.get('_links', '').get('deeplink', '').get(
                'href')
            s.description = series.get('description')
            s.thumb = series.get('thumbnail')
            s.num_episodes = 0
            s.from_serieslist = True
            s.fanart = fanart
            sorted_programs.append(s)

    return sorted_programs


def parse_livestreams_from_feed(data):
    collection_json_data = json.loads(data)['_embedded'].get('collections')

    for collection in collection_json_data:
        if collection.get('title'):
            if 'watch abc channels live' in collection['title'].lower():
                collection_id = collection.get('id')
    import resources.lib.comm as comm
    data = comm.fetch_url(config.API_BASE_URL.format(
        path='/v2/collection/{0}'.format(collection_id)))
    json_data = json.loads(data)
    programs_list = []

    for item in json_data.get('items'):
        if item.get('type') != 'livestream':
            continue
        p = classes.Program()
        title = item.get('showTitle')
        p.title = title
        p.house_number = item.get('houseNumber')
        p.description = item.get('description')
        p.thumb = item.get('thumbnail')
        p.fanart = item.get('thumbnail')
        p.url = item['_links']['self'].get('href')
        p.rating = item.get('classification')
        p.duration = item.get('duration')
        p.captions = item.get('captions')
        p.set_date(item.get('pubDate'))
        p.set_expire(item.get('expireDate'))
        programs_list.append(p)
    return programs_list


def parse_stream_from_json(data):
    p = classes.Program()
    p.title = data.get('showTitle')
    subtitle = data.get('title')
    title_match = match_season_episode(subtitle)
    set_episode_title_from_match(p, title_match, subtitle)
    p.description = data.get('description')
    p.thumb = data.get('thumbnail')
    p.fanart = data.get('thumbnail')
    p.rating = data.get('classification')
    p.duration = data.get('duration')
    p.set_date(data.get('pubDate'))
    p.set_expire(data.get('expireDate'))
    p.captions = data.get('captions') and data.get('captionsOnAkamai')
    return p


def parse_search_results(data):
    json_data = json.loads(data)
    show_list = []
    for show in json_data['results'].get('items', []):
        if show.get('_entity') == 'show':
            s = classes.Series()
            s.num_episodes = show.get('episodeCount')
            s.title = show.get('title')
            additional_title = ''
            if show.get('status'):
                additional_title = show['status'].get('title', '').lower()
            title_match = re.match(
                '^[Ss]eries\\s?(?P<series>\\w+)', additional_title)
            if title_match:
                s.title += ' Series ' + title_match.groups()[0]
            s.url = show.get('_links', '').get('deeplink', '').get(
                'href')
        elif show.get('_entity') == 'video':
            s = classes.Program()
            s.title = show.get('showTitle')
            s.duration = show.get('duration')
            s.house_number = show.get('houseNumber')
            s.url = show.get('_links').get('self').get('href')
        else:
            continue
        s.description = show.get('title')
        s.thumb = show.get('thumbnail')
        show_list.append(s)
    if len(show_list) == 0:
        s = classes.Series()
        s.title = 'No results!'
        s.num_episodes = 0
        s.dummy = True
        show_list.append(s)
    return show_list
