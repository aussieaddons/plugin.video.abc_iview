#
#  AFL Video
#  Copyright (C) 2015 Andy Botting
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
#

import os
import re
import sys
import json
import urllib2
import socket
import config
import utils
import xbmc

# Filter out username and passwords from log files
LOG_FILTERS = (
    ('//.+?:.+?@', '//[FILTERED_USER]:[FILTERED_PASSWORD]@'),
    ('<user>.+?</user>', '<user>[FILTERED_USER]</user>'),
    ('<pass>.+?</pass>', '<pass>[FILTERED_PASSWORD]</pass>'),
)


def make_request(url):
    """
        Make our JSON request to GitHub
    """
    return urllib2.Request(url, headers={
        "Authorization": "Basic %s" % config.ISSUE_API_AUTH,
        "Content-Type": "application/json",
        "User-Agent": '%s/%s' % (config.ADDON_ID, config.VERSION)
    })


def get_public_ip():
    """
        Try and fetch the public IP of the reporter for logging
        and reporting purposes
    """
    try:
        result = urllib2.urlopen('http://ipecho.net/plain', timeout=5)
        data = str(result.read())
    except:
        return "Unknown (lookup failure)"

    try:
        ip = re.compile(r'(\d+\.\d+\.\d+\.\d+)').search(data).group(1)
    except:
        return "Unknown (parse failure)"

    try:
        hostname = socket.gethostbyaddr(ip)[0]
        return "%s (%s)" % (ip, hostname)
    except:
        return ip


def get_isp():
    """
        Try and fetch the ISP of the reporter for logging
        and reporting purposes
    """
    try:
        result = urllib2.urlopen('http://www.whoismyisp.org', timeout=5)
        data = str(result.read())
    except:
        return "Unknown (lookup failure)"

    try:
        isp = re.compile(r'<h1>(.*)</h1>').search(data).group(1)
    except:
        return "Unknown (parse failure)"

    return isp


def get_xbmc_log():
    """
        Fetch and read the XBMC log
    """
    log_path = xbmc.translatePath('special://logpath')

    if os.path.isfile(os.path.join(log_path, 'kodi.log')):
        log_file_path = os.path.join(log_path, 'kodi.log')
    elif os.path.isfile(os.path.join(log_path, 'xbmc.log')):
        log_file_path = os.path.join(log_path, 'xbmc.log')
    else:
        # No log file found
        return None

    utils.log("Reading log file from \"%s\"" % log_file_path)
    with open(log_file_path, 'r') as f:
        log_content = f.read()
    for pattern, repl in LOG_FILTERS:
        log_content = re.sub(pattern, repl, log_content)
    return log_content


def get_xbmc_version():
    """
        Fetch the XBMC build version
    """
    try:
        return xbmc.getInfoLabel("System.BuildVersion")
    except:
        return 'Unknown'


def fetch_tags():
    """
        Fetch the version tags from GitHub
    """
    return json.load(urllib2.urlopen("%s/tags" % config.GITHUB_API_URL))


def get_versions():
    """
        Assemble a list of version from the tags, and split them into lists
    """
    tags = fetch_tags()
    tag_names = map(lambda tag: tag['name'], tags)
    versions = filter(lambda tag: re.match(r'v(\d+)\.(\d+)(?:\.(\d+))?', tag),
                      tag_names)
    return map(lambda tag: map(lambda v: int(v), tag[1::].split('.')),
               versions)


def get_latest_version():
    """
        Sort the list, and get the latest version
    """
    versions = get_versions()
    return sorted(versions, reverse=True)[0]


def is_latest_version(current_version, latest_version):
    """
        Compare current_version (x.x.x string) and
        latest_version ([x,x,x] list)
    """
    if current_version.startswith('v'):
        current_version = current_version[1::]
    current_version = map(lambda v: int(v), current_version.split('.'))
    return current_version == latest_version


def format_issue(issue_data):
    """
        Build our formatted GitHub issue string
    """
    # os.uname() is not available on Windows, so we make this optional.
    try:
        uname = os.uname()
        os_string = ' (%s %s %s)' % (uname[0], uname[2], uname[4])
    except AttributeError:
        os_string = ''

    content = [
        "*Automatic bug report from end-user.*\n## Environment\n"
        "**Add-on Name:** %s" % config.NAME,
        "**Add-on ID:** %s" % config.ADDON_ID,
        "**Add-on Version:** %s" % config.VERSION,
        "**Kodi Version:** %s" % get_xbmc_version(),
        "**Python Version:** %s" % sys.version.replace('\n', ''),
        "**Operating System:** %s %s" % (sys.platform, os_string),
        "**IP Address:** %s" % get_public_ip(),
        "**ISP:** %s" % get_isp(),
        "**Kodi URL:** %s" % sys.argv[2],
        "**Python Path:**\n```\n%s\n```" % '\n'.join(sys.path),
        "\n## Traceback\n```\n%s\n```" % issue_data,
    ]

    log_url = upload_log()
    if log_url:
        content.append("\n[Full log](%s)" % log_url)

    return "\n".join(content)


def upload_log():
    """
        Upload our full XBMC log as a GitHub gist
    """
    try:
        log_content = get_xbmc_log()
    except Exception as e:
        utils.log("Failed to read log: %s" % e)
        return None

    utils.log("Uploading log file")
    try:
        data = {
            "files": {
                "xbmc.log": {
                    "content": log_content
                }
            }
        }
        response = urllib2.urlopen(make_request(config.GIST_API_URL),
                                   json.dumps(data))
    except urllib2.HTTPError as e:
        print e
        utils.log("Failed to save log: HTTPError %s" % e.code)
        return False
    except urllib2.URLError as e:
        print e
        utils.log("Failed to save log: URLError %s" % e.reason)
        return False
    try:
        return json.load(response)["html_url"]
    except:
        utils.log("Failed to parse API response: %s" % response.read())


def report_issue(issue_data):
    """
        Report our issue to GitHub
    """
    issue_body = format_issue(issue_data)

    try:
        data = {
            "title": "[XBMCBOT] - %s" % issue_data.split('\n')[-2],
            "body": issue_body
        }
        response = urllib2.urlopen(make_request(config.ISSUE_API_URL),
                                   json.dumps(data))
    except urllib2.HTTPError as e:
        utils.log("Failed to report issue: HTTPError %s" % e.code)
        return False
    except urllib2.URLError as e:
        utils.log("Failed to report issue: URLError %s" % e.reason)
        return False
    try:
        return json.load(response)["html_url"]
    except:
        utils.log("Failed to parse API response: %s" % response.read())
