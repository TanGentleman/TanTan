# This file is sensitive.

# SECRET KEY
openai_key = None # Your OpenAI Api Key


# The below is only to utilize functions from Link_Grabber.py, you should be able to safely ignore it if you're not using that file.

### SECRET REDDIT CONFIG
token_needed = None
# This is your reddit token, should look like: '1488117263818-EcDrolQTJqYrOOvmVcKbuN-b61wBB'
reddit_token = None # Change when needed. For now, they are 1 day tokens.

client_id = None # From api prefs page, should look like: client_id = 'T6r296zDgBG9TE6pajzK8x'
client_secret = None # Should look like: client_secret = 'mOIYXJwYOcwh6zLd59J9S4BxAuXVxh'
user_agent = 'Puller' # Change to the 'name' you chose in the reddit api prefs.

# Your reddit username and password. This is needed ONLY to authorize getToken() if you don't yet have one.
username = None # 'YOUR_REDDIT_USERNAME'
password = None # 'myPassIsStronk'

# Do not touch. This is the code for authorizing your reddit credentials and generating a token.
import requests
TokenNotSet = Exception(ValueError)
def getHeaders(token_needed):
    if token_needed == None:
            print('You need a token. Set the value token_needed in config.py to True temporarily.')
            raise(TokenNotSet)
    elif token_needed == True:
        print('If this is your first time running this, fantastic!!')
        print('Make sure to set token_needed to False after getting your token!')
        try:
            tok = getToken()
        except:
            print('Darn! Could not get token. Double check all entered fields are correct')
            raise(ValueError)
    elif token_needed == False:
        tok = reddit_token
    headers = {
            'Authorization': 'bearer ' + tok,
            'User-Agent': user_agent}
    return headers

def getToken():
    required_fields = (username, password, client_id, client_secret, user_agent)
    if all(required_fields) == False:
        print('Please fill out all the required fields: username, password, client_id, client_secret, user_agent')
        raise(ValueError)
    auth = requests.auth.HTTPBasicAuth(client_id, client_secret)

    data = {'grant_type': 'password',
            'username': username,
            'password': password,
            'duration': 'temporary',
            'scope': '*'}

    headers = {'User-Agent': f'{user_agent}'}
    res = requests.post('https://www.reddit.com/api/v1/access_token',
                        auth=auth, data=data, headers=headers)
    try:
        print(res.json())
        TOKEN = res.json()['access_token']
    except:
        print('Welp, something broke, working on a fix')
        return
    print(TOKEN)
    print('Remember to save the new token printed above!')
    # headers = {**headers, **{'Authorization': f'bearer {TOKEN}'}}
    return TOKEN

def first_time_token():
    if token_needed == None:
            print('You need a token. Set the value token_needed in mysecrets.py to True temporarily.')
            return
    if token_needed == True:
        getToken()
    if token_needed == False:
        print('token_needed is False! Change it to True if you need a token')
