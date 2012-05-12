import sys
import traceback
import re
import htmlentitydefs
import cgi
import unicodedata
import urllib

import config

pattern = re.compile("&(\w+?);")

def descape_entity(m, defs=htmlentitydefs.entitydefs):
	# callback: translate one entity to its ISO Latin value
	try:
		return defs[m.group(1)]
	except KeyError:
		return m.group(0) # use as is

def descape(string):
	# Fix the hack back from parsing with BeautifulSoup
	string = string.replace('&#38;', '&amp;')

	return pattern.sub(descape_entity, string)

def get_url(s):
	dict = {}
	pairs = s.lstrip("?").split("&")
	for pair in pairs:
		if len(pair) < 3: continue
		kv = pair.split("=",1)
		k = kv[0]
		v = urllib.unquote_plus(kv[1])
		dict[k] = v
	return dict

def make_url(d):
	pairs = []
	for k,v in d.iteritems():
		k = urllib.quote_plus(k)
		v = str(v)
		v = v.decode("utf-8")
		v = unicodedata.normalize('NFC', v).encode('ascii','ignore')
		v = urllib.quote_plus(v)
		pairs.append("%s=%s" % (k,v))
	return "&".join(pairs)

def log(s):
   print "[%s v%s] %s" % (config.NAME, config.VERSION, s)

def log_error(message=None):
	exc_type, exc_value, exc_traceback = sys.exc_info()
	if message:
		exc_value = message
	print "[%s v%s] ERROR: %s (%d) - %s" % (config.NAME, config.VERSION, exc_traceback.tb_frame.f_code.co_name, exc_traceback.tb_lineno, exc_value)
	print traceback.print_exc()

def dialog_error(msg):
	# Generate a list of lines for use in XBMC dialog
	exc_type, exc_value, exc_traceback = sys.exc_info()
	string = "%s v%s Error\n%s (%d) - %s\n%s" % (
		config.NAME, config.VERSION, exc_traceback.tb_frame.f_code.co_name, 
		exc_traceback.tb_lineno, msg, exc_value
	)
	return string.split("\n")

def dialog_message(msg, title=None):
	if not title:
		title = "%s v%s" % (config.NAME, config.VERSION)
	string = "%s\n%s" % (title, msg)
	return string.split("\n")[:4]
