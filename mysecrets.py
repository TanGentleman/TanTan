# This file is sensitive.
import requests
from config import filepath

# SECRET KEY
openai_key = None # Your OpenAI Api Key


# The below is only to utilize functions from reddit_fetcher.py, you should be able to safely ignore it if you're not using that file.

### Your reddit secret token is stored in TanTan/REDDIT_TOKEN.txt


# This is your reddit token, should look like: '1488117263818-EcDrolQTJqYrOOvmVcKbuN-b61wBB'
try: # see if REDDIT_TOKEN.txt exists
    with open(f'{filepath}/REDDIT_TOKEN.txt', 'r') as f:
        reddit_token = f.read()
except:
    # No REDDIT_TOKEN.txt exists. It was worth a try.
    reddit_token = None

user_agent = 'reddit_fetcher' # Recommended to change to the 'name' you chose in the reddit api prefs.

client_id = None
client_secret = None

# Your reddit username and password. This is needed ONLY to authorize getToken() if you don't yet have one.
username = None
password = None

# Do not touch. This is the code for authorizing your reddit credentials and generating a token.

def write_token_to_file(token):
    with open(f'{filepath}/REDDIT_TOKEN.txt', 'w') as f:
        f.write(token)
    print('Saved your reddit token to to REDDIT_TOKEN.txt! If you prefer, set the variable above and delete the file.')


def getHeaders(token):
    if token is None:
        print('You need a token. Saving one to REDDIT_TOKEN.txt')
        token = getToken()
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
            token = getToken()

    headers = {'Authorization': 'bearer ' + token,
                'User-Agent': user_agent}
    return headers

### SAVES TOKEN TO REDDIT_TOKEN.TXT
def getToken(token = None):
    if type(token) == str:
        try:
            headers = {'Authorization': 'bearer ' + token,
                    'User-Agent': user_agent}
            response = requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)
            if response.status_code == 200:
                print('Token is valid')
                return token
            else:
                print('Token is expired. Fetching new token...')
        except: 
            print('Fetching you a token. Keep this token safe!')
            # Save token to a file with the date it was generated.

    required_fields = (username, password, client_id, client_secret, user_agent)
    if all(required_fields) == False:
        print('Please fill out all the required fields: username, password, client_id, client_secret, user_agent')
        raise ValueError('mysecrets.py missing required fields')

    auth = requests.auth.HTTPBasicAuth(client_id, client_secret)
    data = {'grant_type': 'password',
            'username': username,
            'password': password,
            'duration': 'temporary',
            'scope': '*'}

    headers = {'User-Agent': user_agent}
    res = requests.post('https://www.reddit.com/api/v1/access_token',
                        auth=auth, data=data, headers=headers)
    # Better debugging needed?
    # print(res.json())
    token = res.json()['access_token']
    write_token_to_file(token)
    return token

def get_valid_headers():
    headers = getHeaders(reddit_token)
    return headers
