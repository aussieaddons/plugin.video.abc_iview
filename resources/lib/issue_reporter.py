#
#  ABC iView XBMC Addon
#  Copyright (C) 2012 Andy Botting
#
#  This addon includes code from Network Ten CatchUp TV Video Addon
#  Copyright (c) 2014 Adam Malcontenti-Wilson
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

import os, re, sys
import urllib2, socket
import base64
import config, utils
import xbmc

try:
    import simplejson as json
except ImportError:
    import json

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
        return "Could not fetch IP"

    try:
        ip = re.compile(r'(\d+\.\d+\.\d+\.\d+)').search(data).group(1)
    except:
        return "IP address not returned from lookup"

    try:
        hostname = socket.gethostbyaddr(ip)[0]
        return "%s (%s)" % (ip, hostname)
    except:
        return ip


def get_xbmc_log():
    """ 
        Fetch and read the XBMC log
    """
    log_path = xbmc.translatePath('special://logpath')
    log_file_path = os.path.join(log_path, 'xbmc.log')
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


def format_issue(issue_data):
    """
        Build our formatted GitHub issue string
    """
    content = [
        "*Automatic bug report from end-user.*\n## Environment\n"
        "**Plugin Name:** %s" % config.NAME,
        "**Plugin ID:** %s" % config.ADDON_ID,
        "**Plugin Version:** %s" % config.VERSION,
        "**XBMC Version:** %s" % get_xbmc_version(),
        "**Python Version:** %s" % sys.version.replace('\n', ''),
        "**Operating System:** [%s] %s" % (sys.platform, ' '.join(os.uname())),
        "**IP Address:** %s" % get_public_ip(),
        "**Python Path:**\n```\n%s\n```" % '\n'.join(sys.path),
        "\n## Traceback\n```\n%s\n```" % issue_data,
    ]

    log_url = upload_log()
    if log_url:
        content.append("\n[Full xbmc.log](%s)" % log_url)

    return "\n".join(content)


def upload_log():
    """ 
        Upload our full XBMC log as a GitHub gist
    """
    try:
        log_content = get_xbmc_log()
    except Execption as e:
        utils.log("Failed to read log: %s" % e)
        return None

    utils.log("Uploading xbmc.log")
    try:
        response = urllib2.urlopen(make_request(config.GIST_API_URL), json.dumps({
            "files": {
                "xbmc.log": {
                    "content": log_content
                }
            }
        }))
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
    utils.log("Issue Body: %s" % issue_body)

    try:
        response = urllib2.urlopen(make_request(config.ISSUE_API_URL), json.dumps({
            "title": "End-user bug report",
            "body": issue_body
        }))
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
