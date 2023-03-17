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
max_count = 1500 # Please keep this to a reasonable value (I recommend < 1000 unless experienced or small files)
max_file_size = 10000 # This is in KB: filters out .png, .gif, and .mp4 filetypes above this size when check_size == True.
check_size = False # Set to True to enforce a maximize filesize (performs an additional check, but avoids expensive downloads you may not want).

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
try: # This is to allow for a dev features. Please only modify if you know what you're doing.
    # For example, you can do pip install transformers in terminal, then set dev = True to get some neat prompt tokenizing features.
    from tansecrets import NULL
    dev = True
except:
    dev = False
def get_openai_api_key():
    try:
        from tansecrets import openai_key as key
    except:
        from mysecrets import openai_key as key
    return key
def get_headers():
    try:
        from tansecrets import getHeaders
    except:
        from mysecrets import getHeaders
    return getHeaders()
