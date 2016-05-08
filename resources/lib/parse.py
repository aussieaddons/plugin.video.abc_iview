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

from BeautifulSoup import BeautifulStoneSoup

# This is a throwaway variable to deal with a python bug with strptime:
#   ImportError: Failed to import _strptime because the import lockis
#   held by another thread.
throwaway = time.strptime('20140101', '%Y%m%d')

def parse_config(soup):
    """There are lots of goodies in the config we get back from the ABC.
        In particular, it gives us the URLs of all the other XML data we
        need.
    """
    try:
        soup = soup.replace('&amp;', '&#38;')
        xml = BeautifulStoneSoup(soup)

        # should look like "rtmp://cp53909.edgefcs.net/ondemand"
        # Looks like the ABC don't always include this field.
        # If not included, that's okay -- ABC usually gives us the server in the auth result as well.
        rtmp_url = xml.find('param', attrs={'name':'server_streaming'}).get('value')
        rtmp_chunks = rtmp_url.split('/')

        return {
            'rtmp_url'  : rtmp_url,
            'rtmp_host' : rtmp_chunks[2],
            'rtmp_app'  : rtmp_chunks[3],
            'api_url' : xml.find('param', attrs={'name':'api'}).get('value'),
            'categories_url' : xml.find('param', attrs={'name':'categories'}).get('value'),
        }
    except:
        raise Exception("Error fetching iView config. Service possibly unavailable")


def parse_categories(soup):
    categories_list = []

    """
    <category id="pre-school" genre="true">
        <name>ABC 4 Kids</name>
    </category>
    """

    # This next line is the magic to make recursive=False work (wtf?)
    BeautifulStoneSoup.NESTABLE_TAGS["category"] = []
    xml = BeautifulStoneSoup(soup)

    # Get all the top level categories, except the alphabetical ones
    for cat in xml.find('categories').findAll('category', recursive=False):

        id = cat.get('id')
        if cat.get('index') or id == 'index':
            continue

        item = {}
        item['keyword'] = id
        item['name']    = cat.find('name').string;

        categories_list.append(item);

    return categories_list

def parse_programme_from_feed(data):
    xml = ET.fromstring(data)
    show_list = []

    for item in xml.getiterator('item'):

        title = item.find('title').text
        if title.startswith('Trailer'):
            continue

        show = None
        for s in show_list:
            if s.title == title:
               show = s
               break

        if show:
            show.increment_num_episodes()
        else:
            show = classes.Series()
            show.title = title
            show.description = item.find('description').text
            show.thumbnail = item.find('{http://search.yahoo.com/mrss/}thumbnail').attrib['url']
            show_list.append(show)

    return show_list

def parse_programs_from_feed(data):

    xml = ET.fromstring(data)

    programs_list = []
    for item in xml.getiterator('item'):
        p = classes.Program()

        title = item.find('title').text
        p.title = title

        subtitle = item.find('subtitle').text

        title_match = None
        title_parts = None

        if subtitle:
            # Series 2 Episode 25 Home Is Where The Hatch Is
            title_match = re.search('^[Ss]eries\s?(?P<series>\w+)\s[Ee]p(isode)?\s?(?P<episode>\d+)\s(?P<episode_title>.*)$', subtitle)
            if not title_match:
                # Series 8 Episode 13
                title_match = re.search('^[Ss]eries\s?(?P<series>\w+)\s[Ee]p(isode)?\s?(?P<episode>\d+)$', subtitle)
            if not title_match:
                # Episode 34 Shape Shifter
                title_match = re.search('^[Ee]p(isode)?\s?(?P<episode>\d+)\s(?P<episode_title>.*)$', subtitle)
            if not title_match:
                # Series 10 Rylan Clark, Joanna Lumley, Ant And Dec, The Vaccines
                title_match = re.search('^[Ss]eries\s?(?P<series>\d+)\s(?P<episode_title>.*)$', subtitle)
            if not title_match:
                # Episode 5
                title_match = re.search('^[Ee]p(isode)?\s?(?P<episode>\d+)$', subtitle)
            if not title_match:
                p.episode_title = subtitle

            if title_match:
                title_parts = title_match.groupdict()
                p.episode_title = title_parts.get('episode_title')

        try:
            # If we have actual series/episode fields given
            p.series        = item.find('series').text
            p.episode       = item.find('episode').text
        except:
            try:
                # If we only get series/episode in the subtitle
                p.series        = title_parts.get('series')
                p.episode       = title_parts.get('episode')
            except:
                pass

        p.description   = item.find('description').text
        p.url           = item.find('{http://www.abc.net.au/tv/mrss}videoAsset').text
        p.thumbnail     = item.find('{http://search.yahoo.com/mrss/}thumbnail').attrib['url']

        try:
            p.rating = item.find('{http://www.abc.net.au/tv/mrss}rating').text
        except:
            # Rating not given for all programs
            pass

        try:
            duration = item.find('{http://search.yahoo.com/mrss/}content').attrib['duration']
            p.duration = int(duration)
        except:
            utils.log("Couldn't parse program duration: %s" % duration)

        p.date = utils.get_datetime(item.find('pubDate').text)
        p.expire = utils.get_datetime(item.find('{http://www.abc.net.au/tv/mrss}expireDate').text)

        programs_list.append(p)

    return programs_list



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
        result += str(count) + '\n'
        result += convert_timecode(elem.get('start'), elem.get('end'))+'\n'
        st = elem.text.split('|')
        for line in st:
            result += line + '\n'
        result += '\n'
        count +=1
    return result.encode('utf-8')

