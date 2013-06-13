#!/usr/bin/env python

import os
import zipfile
import shutil
import glob
from xml.dom.minidom import parse

ADDON='plugin.video.abc-iview'
EXCLUDE_EXTS = ['.pyc', '.pyo', '.swp']

# Exclude these in modern zip files. They're only needed for XBMC Eden (xbmc4xbox)
EXCLUDE_FILES = ['BeautifulSoup.py']
EXCLUDE_DIRS = ['simplejson']

# Parse addon.xml for version number
dom = parse("%s/addon.xml" % ADDON)
addon = dom.getElementsByTagName('addon')[0]
version = addon.getAttribute('version')
zfilename = "plugin.video.abc_iview-%s.zip" % version

# Walk the directory to create the zip file
print("Writing ZIP file: %s" % zfilename)
z = zipfile.ZipFile(zfilename, 'w')
for r, d, f in os.walk(ADDON):
  for ff in f:
    skip = False

    # If it's not one of the files we're excluding
    for ext in EXCLUDE_EXTS:
      if ff.endswith(ext):
        skip = True

    # Skip any files
    for fn in EXCLUDE_FILES:
      if ff == fn:
        skip = True

    # Skip any directories
    for dr in EXCLUDE_DIRS:
      if r.endswith(dr):
        skip = True

    if not skip: 
      z.write(os.path.join(r, ff), os.path.join(r, ff))
z.close()


# Build XBMC Eden plugin for XBOX
EDEN_PLUGIN = 'ABC iView'
zfilename = "plugin.video.abc_iview-%s_XBOX.zip" % version

# Copy our tree to new directory name
shutil.copytree(ADDON, EDEN_PLUGIN)

# Walk the directory to create the zip file
print("Writing ZIP file: %s" % zfilename)
z = zipfile.ZipFile(zfilename, 'w')
for r, d, f in os.walk(EDEN_PLUGIN):
  for ff in f:
    skip = False

    # If it's not one of the files we're excluding
    for ext in EXCLUDE_EXTS:
      if ff.endswith(ext):
        skip = True

    if not skip: 
      z.write(os.path.join(r, ff), os.path.join(r, ff))
z.close()

# Clean up
shutil.rmtree(EDEN_PLUGIN)
