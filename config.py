filepath = 'Documents/Github/Api_Magic/Chatbot'

### REDDIT CONFIG

DELIMITER = '*;;*' # I recommend not touching this one. Everything's on you if you do.
token_needed = False # set to true before running for first time
debug = False
max_count = 150 # Increase with care

folder_name = 'MY_FOLDER_NAME'
limit_qty = 5
user_input = 'r/WhatsWrongWithYourDog'

#sort_types = ['new', 'top']
#time_periods = ['all', 'year', 'month', 'week', 'day', 'hour']
sort_type = 'new'
time_period = 'week'

# Do not touch. 
import mysecrets
def get_openai_api_key():
    return mysecrets.openai_key

getHeaders = mysecrets.getHeaders
getToken = mysecrets.getToken
