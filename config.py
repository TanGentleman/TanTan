'''Hi there! Hopefully these don't look too scary. The filepath is the location 
where you installed this repository.'''

filepath = 'Documents/Github/Api_Magic'
reddit_folder_name = 'ScrapeAndSpreddit'

### REDDIT CONFIG
image_only = True # Set to False to allow mp4 filetypes. This will not scrape videos hosted by third parties (i.e youtube, tiktok)
max_count = 500 # Please keep this to a reasonable value (I recommend < 1000 unless experienced or small files)


debug = False
limit_qty = 69
user_input = 'r/anarchychess'

# Valid sort types: ['new', 'top']
# Valid time periods = ['all', 'year', 'month', 'week', 'day', 'hour']
sort_type = 'top'
time_period = 'year'

allow_files_over_10MB = True



# Do not touch. 
DELIMITER = '_||_' # Change only if you're certain it won't be affected by text in title/url pairs.
TanEx = Exception(ValueError)
import mysecrets
def get_openai_api_key():
    return mysecrets.openai_key

getHeaders = mysecrets.getHeaders
getToken = mysecrets.getToken
token_needed = False # Please generate a token using mysecrets.py and leave this as False.
