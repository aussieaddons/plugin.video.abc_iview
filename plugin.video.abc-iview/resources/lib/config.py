import os

NAME = 'ABC iView'
VERSION = '1.1.0'

api_version = 383

# os.uname() is not available on Windows, so we make this optional.
try:
	uname = os.uname()
	os_string = ' (%s %s %s)' % (uname[0], uname[2], uname[4])
except AttributeError:
	os_string = ''

user_agent = '%s plugin for XBMC %s%s' % (NAME, VERSION, os_string)

config_url = 'http://www.abc.net.au/iview/xml/config.xml?r=%d' % api_version
auth_url   = 'http://tviview.abc.net.au/iview/auth/?v2'
series_url = 'http://www.abc.net.au/iview/api/series_mrss.htm?id=%s'

akamai_playpath_prefix = 'flash/playback/_definst_/'

# Used for "SWF verification", a stream obfuscation technique
swf_hash    = '96cc76f1d5385fb5cda6e2ce5c73323a399043d0bb6c687edd807e5c73c42b37'
swf_size    = '2122'
swf_url     = 'http://www.abc.net.au/iview/images/iview.jpg'

