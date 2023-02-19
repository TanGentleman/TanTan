'''Hi there! Hopefully these don't look too scary. The filepath is the location 
where you installed this repository.'''

filepath = 'Documents/Github/Api_Magic'
reddit_folder_name = 'ScrapeAndSpreddit'
### REDDIT CONFIG
token_needed = False # Set to True for first use, then to False after you have added your reddit token to mysecrets.py!
image_only = True # Set to False to allow mp4 filetypes.
max_count = 500 # Please keep this to a reasonable value (I recommend < 1000 unless experienced or small files)



# The below 6 variables
debug = False
limit_qty = 6
user_input = 'r/anarchychess'

# Valid sort types: ['new', 'top']
# Valid time periods = ['all', 'year', 'month', 'week', 'day', 'hour']
sort_type = 'top'
time_period = 'month'





# Do not touch. 
DELIMITER = '_||_' # Change if experienced and/or cleverer than me.
TanEx = Exception(ValueError)
import mysecrets
def get_openai_api_key():
    return mysecrets.openai_key

getHeaders = mysecrets.getHeaders
getToken = mysecrets.getToken
