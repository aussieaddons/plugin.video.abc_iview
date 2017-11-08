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
import re
import traceback
import time
from datetime import tzinfo, timedelta, datetime
import htmlentitydefs
import unicodedata
import urllib
import requests
import textwrap
import xbmc
import xbmcgui
import xbmcaddon
import config
import issue_reporter

PATTERN = re.compile("&(\w+?);")


class AUTimeZone(tzinfo):

    def __init__(self, data, reprname, ):
        self.stdoffset = timedelta(hours=data[0], minutes=data[1])
        self.reprname = reprname
        self.data = data

    def __repr__(self):
        return self.reprname

    def first_sunday_on_or_after(self, dt):
        days_to_go = 6 - dt.weekday()
        if days_to_go:
            dt += timedelta(days_to_go)
        return dt

    def utcoffset(self, dt):
        return self.stdoffset + self.dst(dt)

    def dst(self, dt):
        ZERO = timedelta(0)
        DELTA = timedelta(hours=self.data[2]-self.data[0],
                          minutes=self.data[3]-self.data[1])
        if dt is None or dt.tzinfo is None:
            return ZERO

        dststart, dstend = datetime(1, 10, 1, 2), datetime(1, 4, 1, 2)
        start = self.first_sunday_on_or_after(dststart.replace(year=dt.year))
        end = self.first_sunday_on_or_after(dstend.replace(year=dt.year))

        if end <= dt.replace(tzinfo=None) < start:
            return ZERO
        else:
            return DELTA


def get_version():
    addon = xbmcaddon.Addon()
    return addon.getAddonInfo('version')


def get_manual_time(timestamp):
    ts_format = '%a, %d %b %Y %H:%M:%S GMT'
    try:
        res = requests.get('http://freegeoip.net/json/')
        res.raise_for_status()
        tz_string = res.json()['time_zone']
        tz_data = config.TZ_LIST[tz_string]
        UTC = AUTimeZone([0, 0, 0, 0], 'UTC')
        local_timezone = AUTimeZone(tz_data, tz_string)
    except requests.exceptions.HTTPError as e:
        raise e
    try:
        dt = datetime.strptime(timestamp, ts_format, tzinfo=UTC)
    except TypeError:
        dt = datetime(*(time.strptime(timestamp, ts_format)[0:6]), tzinfo=UTC)

    dt = dt.astimezone(local_timezone)
    return str(int(time.mktime(dt.timetuple())))


def get_datetime(timestamp):
    # 2016-04-18 07:00:00
    try:
        dt = time.mktime(time.strptime(timestamp, '%Y-%m-%d %H:%M:%S'))
        return datetime.fromtimestamp(dt)
    except:
        log_error("Couldn't parse timestamp: %s" % timestamp)
    return


def descape_entity(m, defs=htmlentitydefs.entitydefs):
    # callback: translate one entity to its ISO Latin value
    try:
        return defs[m.group(1)]
    except KeyError:
        return m.group(0)  # use as is


def descape(string):
    # Fix the hack back from parsing with BeautifulSoup
    string = string.replace('&#38;', '&amp;')
    return PATTERN.sub(descape_entity, string)


def get_url(s):
    dict = {}
    pairs = s.lstrip("?").split("&")
    for pair in pairs:
        if len(pair) < 3:
            continue
        kv = pair.split("=", 1)
        k = kv[0]
        v = urllib.unquote_plus(kv[1])
        dict[k] = v
    return dict


def make_url(d):
    pairs = []
    for k, v in d.iteritems():
        k = urllib.quote_plus(k)
        # Values can possibly be - UTF-8 as an ASCII str, ASCII as an ASCII
        # str, or unicode. Want clean ASCII for URL.
        if not isinstance(v, unicode):
            v = str(v)
            v = v.decode('utf-8')
        v = unicodedata.normalize('NFC', v).encode('ascii', 'ignore')
        v = urllib.quote_plus(v)
        pairs.append("%s=%s" % (k, v))
    return "&".join(pairs)


def log(s):
    xbmc.log("[%s v%s] %s" % (config.NAME, get_version(), s),
             level=xbmc.LOGNOTICE)


def log_error(message=None):
    exc_type, exc_value, exc_tb = sys.exc_info()
    if message:
        exc_value = message
    xbmc.log("[%s v%s] ERROR: %s (%d) - %s" %
             (config.NAME, get_version(),
              exc_tb.tb_frame.f_code.co_name, exc_tb.tb_lineno, exc_value),
             level=xbmc.LOGERROR)


def dialog_error(err=None):
    # Generate a list of lines for use in XBMC dialog
    content = []
    exc_type, exc_value, exc_tb = sys.exc_info()
    content.append("%s v%s Error" % (config.NAME, get_version()))
    content.append(str(exc_value))
    return content


def dialog_message(msg, title=None):
    if not title:
        title = "%s v%s" % (config.NAME, get_version())
    # Add title to the first pos of the textwrap list
    content = textwrap.wrap(msg, 60)
    content.insert(0, title)
    return content


def get_platform():
    """ Work through a list of possible platform types and return the first
        match. Ordering of items is important as some match more thant one
        type.

        E.g. Android will match both Android and Linux
    """
    platforms = [
        "Android",
        "Linux.RaspberryPi",
        "Linux",
        "XBOX",
        "Windows",
        "ATV2",
        "IOS",
        "OSX",
        "Darwin",
    ]

    for platform in platforms:
        if xbmc.getCondVisibility('System.Platform.'+platform):
            return platform
    return "Unknown"


def get_xbmc_build():
    return xbmc.getInfoLabel("System.BuildVersion")


def get_xbmc_version():
    build = get_xbmc_build()
    # Keep the version number, and strip the rest
    version = build.split(' ')[0]
    return version


def get_xbmc_major_version():
    """ Return the major version number of the running XBMC
    """
    version = get_xbmc_version().split('.')[0]
    return int(version)


def log_xbmc_platform_version():
    """ Log our XBMC version and platform for debugging
    """
    version = get_xbmc_version()
    platform = get_platform()
    log("XBMC/Kodi %s running on %s" % (version, platform))


def get_file_dir():
    """ Make our addon working directory if it doesn't exist and
        return it.
    """
    filedir = os.path.join(xbmc.translatePath('special://temp/'),
                           config.ADDON_ID)
    if not os.path.isdir(filedir):
        os.mkdir(filedir)
    return filedir


def save_last_error_report(trace):
    """ Save a copy of our last error report
    """
    try:
        rfile = os.path.join(get_file_dir(), 'last_report_error.txt')
        with open(rfile, 'w') as f:
            f.write(trace)
    except:
        log("Error writing error report file")


def can_send_error(trace):
    """ Check to see if our new error message is different from the last
        successful error report. If it is, or the file doesn't exist, then
        we'll return True
    """
    try:
        rfile = os.path.join(get_file_dir(), 'last_report_error.txt')

        if not os.path.isfile(rfile):
            return True
        else:
            f = open(rfile, 'r')
            report = f.read()
            if report != trace:
                return True
    except:
        log("Error checking error report file")

    log("Not allowing error report. Last report matches this one")
    return False


def handle_error(err=None):
    traceback_str = traceback.format_exc()
    log(traceback_str)
    report_issue = False

    # Don't show any dialogs when user cancels
    if 'SystemExit' in traceback_str:
        return

    d = xbmcgui.Dialog()
    if d:
        message = dialog_error(err)

        # Work out if we should allow an error report
        send_error = can_send_error(traceback_str)

        # Some transient network errors we don't want any reports about
        ignore_errors = ['The read operation timed out',
                         'IncompleteRead',
                         'getaddrinfo failed',
                         'No address associated with hostname',
                         'Connection reset by peer',
                         'HTTP Error 404: Not Found']

        if any(s in traceback_str for s in ignore_errors):
            send_error = False

        if send_error:
            latest_version = issue_reporter.get_latest_version()
            version_string = '.'.join([str(i) for i in latest_version])
            if not issue_reporter.is_latest_version(get_version(),
                                                    latest_version):
                message.append('Your version of this add-on is outdated. '
                               'Please try upgrading to the latest version: '
                               'v%s' % version_string)
                d.ok(*message)
                return

            # Only report if we haven't done one already
            try:
                message.append('Would you like to automatically '
                               'report this error?')
                report_issue = d.yesno(*message)
            except:
                message.append('If this error continues to occur, '
                               'please report it to our issue tracker.')
                d.ok(*message)
        else:
            # Just show the message
            d.ok(*message)
    if report_issue:
        log("Reporting issue to GitHub...")
        issue_url = issue_reporter.report_issue(traceback_str)
        if issue_url:
            # Split the url here to make sure it fits in our dialog
            split_url = issue_url.replace('/xbmc', ' /xbmc')
            d.ok('%s v%s Error' % (config.NAME, get_version()),
                 'Thanks! Your issue has been reported to: %s' % split_url)
            # Touch our file to prevent more than one error report
            save_last_error_report(traceback_str)
