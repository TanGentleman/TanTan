# Tests
# This file is still being created
import mysecrets as m
import config as c

def reddit_configuration_exists():
    return all(m.token_needed, m.reddit_token, m.client_id, m.client_secret, m.user_agent, m.username, m.password)

def get_a_token():
    m.first_time_token()

if __name__ == '__main__':
    if reddit_configuration_exists():
        print('Reddit configuration exists')
        get_a_token()
    else:
        print('Reddit configuration is incomplete')
