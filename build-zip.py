#!/usr/bin/env python

import os
import zipfile
import shutil
import glob
from xml.dom.minidom import parse

ADDON='plugin.video.abc-iview'

# Exclude these in modern zip files. They're only needed for XBMC Eden (xbmc4xbox)
EXCLUDE_EXTS = ['.pyc', '.pyo', '.swp', '.zip', '.gitignore']
EXCLUDE_FILES = ['build-zip.py']
EXCLUDE_DIRS = ['.git']

# Parse addon.xml for version number
dom = parse("addon.xml")
addon = dom.getElementsByTagName('addon')[0]
version = addon.getAttribute('version')

zfilename = "plugin.video.abc_iview-%s.zip" % version
print("Writing ZIP file: %s" % zfilename)
# Walk the directory to create the zip file
z = zipfile.ZipFile(zfilename, 'w')
for r, d, f in os.walk('.'):
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
      if (r.find(dr) > -1) or (r.find('deps') > -1):
        skip = True

    if not skip: 
      z.write(os.path.join(r, ff), os.path.join(ADDON, r, ff), zipfile.ZIP_DEFLATED)
z.close()

# Build XBMC Eden plugin for XBOX
EDEN_PLUGIN = 'ABC iView'
zfilename = "plugin.video.abc_iview-%s_XBOX.zip" % version

# Walk the directory to create the zip file
print("Writing ZIP file: %s" % zfilename)
z = zipfile.ZipFile(zfilename, 'w')
for r, d, f in os.walk('.'):
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
      if r.find(dr) > -1:
        skip = True

    if not skip:
      z.write(os.path.join(r, ff), os.path.join(EDEN_PLUGIN, r, ff), zipfile.ZIP_DEFLATED)
z.close()
