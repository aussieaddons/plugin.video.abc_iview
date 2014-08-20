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

import os, sys

# Add our resources/lib to the python path
try:
   current_dir = os.path.dirname(os.path.abspath(__file__))
except:
   current_dir = os.getcwd()

sys.path.append(os.path.join(current_dir, 'resources', 'lib'))
import utils, categories, series, programs, play

# Print our platform/version debugging information
utils.log_xbmc_platform_version()

if __name__ == "__main__" :
   params_str = sys.argv[2]
   params = utils.get_url(params_str)

   if (len(params) == 0):
      categories.make_category_list()
   elif params.has_key("play"):
      play.play(params_str)
   elif params.has_key("series"):
      programs.make_programs_list(params_str)
   elif params.has_key("category"):
      series.make_series_list(params_str)
