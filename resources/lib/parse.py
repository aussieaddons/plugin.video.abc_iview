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

import comm
import config
import classes
import utils
import sys
import re
import datetime
import time
import json

import xml.etree.ElementTree as ET

def parse_categories(config):
    """ Fetch navigation json file and retrieve channels and categories.
    """
    categories_list = []
    data = json.loads(config)
    categories = [x for y in [data[1]['submenus'][0]['channels'], 
                data[1]['submenus'][1]['submenus']] for x in y]    
    
    for cat in categories:
        item = {}
        item['path'] = cat['path']
        item['name'] = cat['title']
        categories_list.append(item)

    return categories_list

def parse_programme_from_feed(data):
    jsondata = json.loads(data)
    show_list = []
    href_list = []
    show_index = json.loads(comm.fetch_url(config.index_url))
    series_houseno_list = [(x['href'][-13:-6], x['episodeCount']) 
                    for item in show_index['index'] for x in item['episodes']]
    
    for section in jsondata[u'index']:
        for item in section[u'episodes']:
            
            title = item[u'seriesTitle']
            if title.startswith(u'Trailer'):
                continue
            
            show = classes.Series()
            
            show.series_houseno = item['episodeHouseNumber'][:7]
            
            episode_count = 0
            for houseno in series_houseno_list:
                if houseno[0] == show.series_houseno:
                    episode_count = houseno[1]
                    show.num_episodes = episode_count
                    break
            if episode_count == 0: #some shows have multiple house no's
                for group in show_index['index']:
                    for listing in group['episodes']:
                        if listing['seriesTitle'] == title:
                            show.num_episodes = listing['episodeCount']
                            break
                    break
            show.title = title
            if u'title' in item:
                show.description = item[u'title']
                title_match = re.match('^[Ss]eries\s?(?P<series>\w+)', show.description)
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
    related = config.feed_url.format(jsondata['related'])
    
    programs_list = []
    related_list = []
    related_list.append(jsondata)
    
    if int(episode_count) > 1:
        comm.download_related_list(parse_other_episodes(related), related_list)
    
    for item in related_list:
        p = classes.Program()
        subtitle = None
        if 'title' in item:
            title = item['seriesTitle']
            subtitle = item['title']
            p.title = title
            p.episode_title = subtitle
        else:
            title = item['seriesTitle']
            p.title = title           
        
        p.house_number  = item['episodeHouseNumber']
        p.description   = item['description']
        p.url           = item['playlist'][-1]['hls-high']
        p.thumbnail     = item['thumbnail']

        try:
            p.rating = item['rating']
        except:
            # Rating not given for all programs
            pass

        try:
            duration = item['duration']
            p.duration = int(duration)
        except:
            if 'duration' in locals():
                utils.log("Couldn't parse program duration: %s" % duration)
            
        try:
            p.subtitle_url = item['playlist'][-1]['captions']['src-xml']
        except:
            pass

        p.date = utils.get_datetime(item['pubDate'])
        p.expire = utils.get_datetime(item['expireDate'])

        programs_list.append(p)
    
    sorted_programs = sorted(programs_list, key=lambda x: x.get_date_time(), reverse=True)
    return sorted_programs

def parse_other_episodes(url):
    """ return a list of URLs linking to other shows in series"""
    data = json.loads(comm.fetch_url(url))
    
    related_list = []
    
    for episode in data['index'][0]['episodes']:
        related_list.append(episode['href'])
    return related_list


def convert_timecode(start, end):
    """ convert iview xml timecode attribute to subrip srt standard"""
    return start[:8]+','+start[9:11]+'0'+' --> '+end[:8]+','+end[9:11]+'0'


def convert_to_srt(data):
    """ convert our iview xml subtitles to subrip SRT format"""
    tree = ET.fromstring(data)
    root = tree.find('reel')
    result = ""
    count = 1
    for elem in root.findall('title'):
        if elem.text == None:
            continue
        result += str(count) + '\n'
        result += convert_timecode(elem.get('start'), elem.get('end'))+'\n'
        st = elem.text.split('|')
        for line in st:
            result += line + '\n'
        result += '\n'
        count +=1
    return result.encode('utf-8')

