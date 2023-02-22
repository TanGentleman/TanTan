# Tests
import mysecrets as m
import config as c

def reddit_configuration_exists():
    return all(m.token_needed, m.reddit_token, m.client_id, m.client_secret, m.user_agent, m.username, m.password)

def openai_configuration_exists():
    return m.openai_key or 'OpenAI API Key not found'

def config_py_ready():
    return False or 'Config.py looks good to go!'

def main():
    m.first_time_token()

if __name__ == '__main__':
    main()