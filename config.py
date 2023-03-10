'''Hi there! Hopefully these don't look too scary. The filepath is the location 
where you installed this repository. I recommend the Desktop, so ~/Desktop/TanTan'''

FILEPATH = 'Desktop/TanTan' # Relative to your home directory. Do not include a trailing slash.

from os import getcwd
if 'TanTan'.lower() in getcwd().lower():
    # User is currently in the repository folder
    filepath = ''
else:
    # User is not currently in the repository folder. Set path to FILEPATH constant above
    filepath = FILEPATH

reddit_folder_name = 'ScrapeAndSpreddit'

### REDDIT CONFIG
image_only = True # Set to False to allow mp4 filetypes. This will not scrape videos hosted by third parties (i.e youtube, tiktok)
max_count = 500 # Please keep this to a reasonable value (I recommend < 1000 unless experienced or small files)
max_file_size = 10000 # This is in KB, only filters valid .gif and .mp4 filetypes.


# The following variables can also optionally be set when running reddit_fetcher.py via the command line
# [MAGIC STRING] = {u/user or r/subreddit} {qty} {new/top} {all/year/month/week/day/hour} {-d for debug}
# The terminal command for the following configuration would be:
# python3 path/to/TanTan/reddit_fetcher.py r/anarchychess 69 top year
user_input = 'r/anarchychess'
limit_qty = 69

sort_type = 'top' # Valid sort types: ['new', 'top']
time_period = 'year' # Valid time periods = ['all', 'year', 'month', 'week', 'day', 'hour']
debug = False

# Do not touch. 
DELIMITER = '_||_' # Change only if you're certain it won't be affected by text in title/url pairs.

try: # This is a hacky way to allow for a dev environment. Please do not touch.
    import tansecrets as m
    dev = True
except:
    import mysecrets as m
    dev = False
def get_openai_api_key():
    return m.openai_key

get_headers = m.get_valid_headers
