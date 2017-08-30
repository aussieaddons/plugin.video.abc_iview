#
#  ABC iView XBMC Addon
#  Copyright (C) 2012 Andy Botting
#
#  This addon includes code from python-iview
#  Copyright (C) 2009-2012 by Jeremy Visser <jeremy@visser.name>
#
#  This addon is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This addon is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this addon. If not, see <http://www.gnu.org/licenses/>.
#

import classes
import comm
import config
import datetime
import json
import re
import time
import xbmcaddon
import xml.etree.ElementTree as ET

from aussieaddonscommon import utils


def get_datetime(timestamp):
    """Parse timestamp into a datetime"""
    try:
        dt = time.mktime(time.strptime(timestamp, '%Y-%m-%d %H:%M:%S'))
        return datetime.datetime.fromtimestamp(dt)
    except Exception:
        utils.log_error("Couldn't parse timestamp: %s" % timestamp)
    return


def parse_categories(config):
    """Fetch navigation json file and retrieve channels and categories."""
    categories_list = []
    data = json.loads(config)
    categories = [x for y in [data[1]['submenus'][0]['channels'],
                  data[1]['submenus'][1]['submenus']] for x in y]

    for cat in categories:
        item = {}
        item['path'] = cat['path']
        item['name'] = cat['title']
        if 'logoUrl' in cat:
            item['thumbnail'] = cat['logoUrl']
        categories_list.append(item)

    return categories_list


def parse_programme_from_feed(data, keyword):
    jsondata = json.loads(data)
    show_list = []
    href_list = []
    show_index = json.loads(comm.fetch_url(config.INDEX_URL))
    series_houseno_list = [(x['href'][-13:-6], x['episodeCount'])
                           for item in show_index['index']
                           for x in item['episodes']]

    for section in jsondata[u'index']:
        for item in section[u'episodes']:

            houseno = item['episodeHouseNumber'][:7]
            title = item[u'seriesTitle']
            if title.startswith(u'Trailer'):
                continue

            show = None
            if keyword == 'category/news' or keyword == 'channel/news24':
                for s in show_list:
                    if s.series_houseno == houseno:
                        show = s
                        break
                    if s.title == title:
                        show = s
                        break

            if not show:
                show = classes.Series()
                show.series_houseno = houseno
                episode_count = 0
                for houseno in series_houseno_list:
                    if houseno[0] == show.series_houseno:
                        episode_count = houseno[1]
                        show.num_episodes = episode_count
                        break
                # some shows have multiple house no's, try matching titles
                if episode_count == 0:
                    for group in show_index['index']:
                        for listing in group['episodes']:
                            if listing['seriesTitle'] == title:
                                show.num_episodes = listing['episodeCount']
                                break

                show.title = title
                if u'title' in item:
                    show.description = item[u'title']
                    title_match = re.match(
                        '^[Ss]eries\s?(?P<series>\w+)', show.description)
                    if title_match:
                        show.title += ' Series ' + title_match.groups()[0]
                else:
                    show.description = item[u'seriesTitle']
                show.thumbnail = item['thumbnail']
                show.series_url = item['href']
                href_list.append(item['href'])
                show_list.append(show)

    return show_list


def parse_programs_from_feed(data, episode_count):
    jsondata = json.loads(data)
    related = config.FEED_URL.format(jsondata['related'])

    programs_list = []
    related_list = []
    related_list.append(jsondata)

    if int(episode_count) > 1:
        comm.fetch_related_list(parse_other_episodes(related), related_list)

    for item in related_list:
        if 'playlist' not in item:
            continue

        p = classes.Program()

        title = item.get('seriesTitle')
        p.title = title

        # Convoluted Season/Episode parsing
        title_match = None
        title_parts = None

        subtitle = item.get('title')
        if subtitle:
            # Series 2 Episode 25 Home Is Where The Hatch Is
            # Series 4 Ep:11 As A Yoga Yuppie
            # Series 4 Ep 10: Emission Impossible
            title_match = re.search('^[Ss]eries\s?(?P<series>\w+):?\s[Ee]p(isode)?:?\s?(?P<episode>\d+):?\s(?P<episode_title>.*)$', subtitle)  # noqa
            if not title_match:
                # Series 8 Episode 13
                # Series 8 Episode:13
                title_match = re.search('^[Ss]eries\s?(?P<series>\w+):?\s?[Ee]p(isode)?:?\s?(?P<episode>\d+)$', subtitle)  # noqa
            if not title_match:
                # Episode 34 Shape Shifter
                # Ep:34 Shape Shifter
                title_match = re.search('^[Ee]p(isode)?:?\s?(?P<episode>\d+):?\s?(?P<episode_title>.*)$', subtitle)  # noqa
            if not title_match:
                # Series 10 Rylan Clark, Joanna Lumley, Ant And Dec
                title_match = re.search('^[Ss]eries:?\s?(?P<series>\d+):?\s(?P<episode_title>.*)$', subtitle)  # noqa
            if not title_match:
                # Episode 5
                # Ep 5
                # Episode:5
                title_match = re.search('^[Ee]p(isode)?:?\s?(?P<episode>\d+)$',
                                        subtitle)
            if not title_match:
                p.episode_title = subtitle

            if title_match:
                title_parts = title_match.groupdict()
                p.episode_title = title_parts.get('episode_title')

        try:
            # If we only get series/episode in the subtitle
            p.series = title_parts.get('series')
            p.episode = title_parts.get('episode')
        except Exception:
            pass

        p.house_number = item.get('episodeHouseNumber')
        p.description = item.get('description')
        p.thumbnail = item.get('thumbnail')
        addon = xbmcaddon.Addon()
        if ('hls-plus' in item['playlist'][-1] and
           addon.getSetting('hd_streams') == 'true'):
            p.url = item['playlist'][-1]['hls-plus']
            p.hq = True
        else:
            p.url = item['playlist'][-1]['hls-high']
        p.rating = item.get('rating')
        p.duration = item.get('duration')

        try:
            p.subtitle_url = item['playlist'][-1]['captions']['src-vtt']
        except Exception:
            pass

        p.date = get_datetime(item.get('pubDate'))
        p.expire = get_datetime(item.get('expireDate'))

        programs_list.append(p)

    sorted_programs = sorted(programs_list,
                             key=lambda x: x.get_date_time(),
                             reverse=True)
    return sorted_programs


def parse_other_episodes(url):
    """Return a list of URLs linking to other shows in series"""
    data = json.loads(comm.fetch_url(url))

    related_list = []

    for episode in data['index'][0]['episodes']:
        related_list.append(episode['href'])
    return related_list


def parse_m3u8_streams(m3u8, quality):
    """Parse m3u8 streams

    Parse the retrieved m3u8 stream list into a list of dictionaries
    then return the url for the highest quality stream. Different
    handling is required of live m3u8 files as they seem to only contain
    the destination filename and not the domain/path.
    """
    data = m3u8.splitlines()
    count = 1
    m3uList = []

    while count < len(data):
        line = data[count]
        line = line.strip('#EXT-X-STREAM-INF:').strip('PROGRAM-ID=1,')
        line = line[:line.find('CODECS')]
        if line.endswith(','):
            line = line[:-1]
        line = line.strip().split(',')
        linelist = [i.split('=') for i in line]
        linelist.append(['URL', data[count+1]])
        m3uList.append(dict((i[0], i[1]) for i in linelist))
        count += 2

    sorted_m3uList = sorted(m3uList, key=lambda k: int(k['BANDWIDTH']))
    stream = sorted_m3uList[int(quality)]['URL']
    return stream


def convert_timecode(start, end):
    """Convert iview xml timecode attribute to subrip srt standard"""
    return start[:8]+','+start[9:11]+'0'+' --> '+end[:8]+','+end[9:11]+'0'


def convert_to_srt(data):
    """Convert our iview xml subtitles to subrip SRT format"""
    tree = ET.fromstring(data)
    root = tree.find('reel')
    result = ""
    count = 1
    for elem in root.findall('title'):
        if elem.text is None:
            continue
        result += str(count) + '\n'
        result += convert_timecode(elem.get('start'), elem.get('end'))+'\n'
        st = elem.text.split('|')
        for line in st:
            result += line + '\n'
        result += '\n'
        count += 1
    return result.encode('utf-8')
