#!/usr/bin/env python

import os
import zipfile
from xml.dom.minidom import parse

ADDON='plugin.video.abc-iview'
EXCLUDE_EXTS = ['.pyc', '.pyo', '.swp']

# Parse addon.xml for version number
dom = parse("%s/addon.xml" % ADDON)
addon = dom.getElementsByTagName('addon')[0]
version = addon.getAttribute('version')
zfilename = "plugin.video.abc_iview-%s.zip" % version

# Walk the directory to create the zip file
z = zipfile.ZipFile(zfilename, 'w')
for r, d, f in os.walk(ADDON):
  for ff in f:
    skip = False

    # If it's not one of the files we're excluding
    for ext in EXCLUDE_EXTS:
      if ff.endswith(ext):
        skip = True

    if not skip: 
      z.write(os.path.join(r, ff), os.path.join(r, ff))
z.close()

