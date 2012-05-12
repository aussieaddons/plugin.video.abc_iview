import os
import sys

# Add our resources/lib to the python path
try:
   current_dir = os.path.dirname(os.path.abspath(__file__))
except:
   current_dir = os.getcwd()

sys.path.append(os.path.join(current_dir, 'resources', 'lib'))

import utils, series, programs, play

utils.log('Initialised')

if __name__ == "__main__" :
   params_str = sys.argv[2]
   params = utils.get_url(params_str)

   if (len(params) == 0):
      series.make_series_list()
   else:
      if params.has_key("series_id"):
         programs.make_programs_list(params_str)
      elif params.has_key("play"):
         play.play(params_str)
