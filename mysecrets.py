# This file is sensitive.
import requests
from config import filepath

# SECRET KEY
openai_key = None # Your OpenAI Api Key
# The below is only to utilize functions from reddit_fetcher.py, you should be able to safely ignore it if you're not using that file.

USER_AGENT = 'reddit_fetcher' # Recommended to change to the 'name' you chose in the reddit api prefs.

CLIENT_ID = None
CLIENT_SECRET = None 

# Your reddit username and password. This is needed ONLY to authorize getToken() if you don't yet have one.
USERNAME = None
PASSWORD = None

### Your reddit secret token is stored in TanTan/REDDIT_TOKEN.txt
# It should look like: '1488117263818-EcDrolQTJqYrOOvmVcKbuN-b61wBB'

try: # see if REDDIT_TOKEN.txt exists
    with open(f'{filepath}/REDDIT_TOKEN.txt', 'r') as f:
        REDDIT_TOKEN = f.read()
except:
    # No REDDIT_TOKEN.txt exists. It was worth a try.
    REDDIT_TOKEN = None


# Do not touch. This is the code for authorizing your reddit credentials and generating a token.
reddit_config = (USER_AGENT, CLIENT_ID, CLIENT_SECRET, USERNAME, PASSWORD)
def write_token_to_file(token):
    with open(f'{filepath}/REDDIT_TOKEN.txt', 'w') as f:
        f.write(token)
    print('Saved your reddit token to to REDDIT_TOKEN.txt! If you prefer, set the variable above and delete the file.')


def getHeaders(token, reddit_config):
    assert(all(reddit_config))
    (user_agent, client_id, client_secret, username, password) = reddit_config
    if token is None:
        print('You need a token. Saving one to REDDIT_TOKEN.txt')
        token = get_reddit_token(user_agent, client_id, client_secret, username, password)
    else:
        try:
            headers = {
                    'Authorization': 'bearer ' + token,
                    'User-Agent': user_agent}
            response = requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)
            if response.status_code == 200:
                print('Token is valid')
        except:
            print('Token is invalid. Fetching new token...')
            token = get_reddit_token(user_agent, client_id, client_secret, username, password)

    headers = {'Authorization': 'bearer ' + token,
                'User-Agent': user_agent}
    return headers

### SAVES TOKEN TO REDDIT_TOKEN.TXT

def get_reddit_token(user_agent, client_id, client_secret, username, password):
    auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    data = {'grant_type': 'password',
            'username': username,
            'password': password,
            'duration': 'temporary',
            'scope': '*'}

    headers = {'User-Agent': user_agent}
    res = requests.post('https://www.reddit.com/api/v1/access_token',
                        auth=auth, data=data, headers=headers)
    try:
        token = res.json()['access_token']
        write_token_to_file(token)
        return token
    except:
        print('Something went wrong. Please check your credentials.')
        raise ValueError('Reddit token validation failed')
