import openai
from mysecrets import openai_key
import sys
import datetime
import time
from os import path

filepath = 'Documents/Github/Api_Mastery'

max_tokens = 150
max_codex = 1000


def read_codex_prompt():
    try:
        contents_path = f'{filepath}/codex_prompt.txt'
        with open(contents_path, 'r') as file:
            file_contents = file.read()
            return file_contents
    except FileNotFoundError:
        print('No codex_prompt.txt in this directory found')

def read_text_prompt():
    try:
        contents_path = f'{filepath}/text_prompt.txt'
        with open(contents_path, 'r') as file:
            file_contents = file.read()
            return file_contents
    except FileNotFoundError:
        print('No text_prompt.txt in this directory found')


def token_count(s:str):
    return len(s.strip().split(' '))
def generate_text(prompt, engine, max_tokens):
    # Set the API key
    openai.api_key = openai_key
    
    # Generate responses using the model
    try:
       response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        max_tokens=max_tokens,
        n=1,
        temperature=0.3
        )
    except openai.error.OpenAIError as e:
        print(e.http_status)
        print(e.error)
        return
    
    return response['choices']

def write_to_log_file(convo, correlates):
    with open(f'{filepath}/v2_logfile_1.txt', 'a') as file:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d')
        file.write(f'Timestamp: {timestamp}\n{convo}\n ==== End of Entry ====\n')
        print('Saved log file.')
    with open(f'{filepath}/v2_correlation_log.txt', 'a') as file:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d')
        file.write(f'Timestamp: {timestamp}\n{correlates}\n ==== End of Entry ====\n')
        print('Saved log file.')

def parse_args():
    ask_engine = False
    ask_token = False
    debug = False
    args = sys.argv
    arg_count = len(args)
    if arg_count > 1:
        for arg in args[1:]:
            if arg == '-d':
                debug = True
            elif arg == 'config':
                ask_engine = True
                ask_token = True
                
        if debug: print(f'{ask_engine}, {ask_token}, {debug}')
        return ask_engine, ask_token, debug
                

def engine_choice(engine_prompt, status):
    if len(engine_prompt) < 2:
        print('Please enter at least two characters')
        raise(ValueError)
    if 'ada'.startswith(engine_prompt):
        engine = 'text-ada-001'
        return engine
    elif 'curie'.startswith(engine_prompt):
        engine = 'text-curie-001'
        return engine
    elif 'davinci'.startswith(engine_prompt):
        if status == 'slow': 
            print('Unavailable, choose a different engine.')
            raise(ValueError)
        else:
            engine = 'text-davinci-003'
            return engine
    elif 'codex'.startswith(engine_prompt):
        if status == 'slow': 
            print('Unavailable, choose a different engine.')
            raise(ValueError)
        else:
            engine = 'code-davinci-002'
            return engine
    else:
        print('invalid')
        raise(ValueError)


def config(ask_engine, ask_token, slow_status, engine, max_tokens):
    if ask_engine:
        legal_answer = False
        while legal_answer == False:
            engine_prompt = ''
            try:
                engine_prompt = input('[ada, curie, davinci, codex] Engine Choice: ')
                engine = engine_choice(engine_prompt, slow_status)
                legal_answer = True
            except:
                print('Not recognized. Try again.')
    if ask_token:
        legal_answer = False
        while legal_answer == False:
            token_prompt = ''
            try:
                token_prompt = input('Max Token count: ')
                token_prompt = int(token_prompt)
                if (token_prompt > 0) and (token_prompt <= 200):
                    max_tokens = token_prompt
                    legal_answer = True
                else:
                    print('Try a value between 1 and 200 for now')
            except:
                print('Not recognized max token value. Try 1-200.')
    return engine, max_tokens

def print_token_info (token_info): 
    (prompt_token_count, response_token_count, history_token_count) = token_info
    print (f'prompt_tokens: {prompt_token_count}, response_tokens: {response_token_count}, history tokens: {history_token_count}')

def interactive_chat(slow_status, max_tokens):
    prompt_token_count = 0
    response_token_count = 0
    history_token_count = 0
    token_info = (prompt_token_count, response_token_count, history_token_count)
    history = ''
    cached_history = ''
    full_log = '' # Includes delimiters and time taken for response
    response_count = 0
    correlation_log = []
    debug = False
    logging_on = True
    prompt_from_file = False
    if slow_status == True:
        engine = 'text-curie-001'
    else:
        engine = 'text-davinci-003'
        
    config_arg = parse_args()
    if config_arg: 
        (ask_engine, ask_token, debug) = config_arg
        if debug: print('beep')
        engine, max_tokens = config(ask_engine, ask_token, slow_status, engine, max_tokens)
    
    full_log += f'Engine set to: {engine}, {max_tokens} Max Tokens\n'
    text_prompt = ''
    replace_input = False
    replace_input_text = ''
    while True:
        #Ask for input
        if replace_input:
            if prompt_from_file:
                prompt = text_prompt
                prompt_from_file = False
            else:
                prompt = replace_input_text
            replace_input = False

        else:
            prompt = input('Enter a prompt: ')
        start = time.time()
        #Escape string (Gives summary too)
        token_info = (prompt_token_count, response_token_count, token_count(history))

        # ESCAPE COMMAND
        if prompt == 'quit':
            print_token_info(token_info)
            full_log += f'prompt_tokens: {prompt_token_count}, response_tokens: {response_token_count}, history tokens: {token_count(history)}'
            return full_log, correlation_log, logging_on

        elif prompt in ['', ' ']:
            print('Type a lil somethin at least')
        elif prompt == 'stats':
            print_token_info (token_info)
            print(f'engine: {engine}, max_tokens = {max_tokens}')
        elif prompt == 'config':
            engine, max_tokens = config(True, True, slow_status, engine, max_tokens)
            msg = f'Engine set to: {engine}, {max_tokens} Max Tokens\n'
            print(msg)
            full_log += msg
        elif prompt == 'help':
            print('Available commands: help, quit, status, config, history, forget, del')
        elif prompt == 'history':
            print(f'history shown below:\n{(history)}')
        elif prompt == 'forget':
            history = ''
            msg = '<History has been erased. Please continue the conversation fresh :)>\n'
            print(msg)
            full_log += msg
        elif prompt == 'del':
            history = cached_history
            msg = '<I have deleted the last exchange from my memory>\n'
            print(msg)
            full_log += msg
        elif prompt == 'log':
            history = cached_history
            if logging_on:
                msg = '<Logging disabled> Conversation will not be stored.\n'
                print(msg)
                logging_on = False
            else:
                '<Logging enabled> Conversation WILL be stored.\n'
                print(msg)
                logging_on = True
        elif prompt == 'read':
            if path.isfile(f'{filepath}/text_prompt.txt'):
                text_prompt = read_text_prompt()
                prompt_from_file = True
                continue
            else:
                print('You have not written a text_prompt.txt file for me to read. I gotchu.')
                with open(f'{filepath}/text_prompt.txt', 'w') as file:
                    file.write('Insert text prompt here')
            continue

        elif prompt == 'codex':
            print(f'Trying codex!')
            if path.isfile(f'{filepath}/codex_prompt.txt'):
                pass
            else:
                print('You have not written a codex_prompt.txt file for me to read. I gotchu.')
                with open(f'{filepath}/codex_prompt.txt', 'w') as file:
                    file.write('Please create the following function with comments in Python:\n' +
                                    'def myFunc():\n\t#Do THIS\nSeed Text: It should be optimized for performance and readability.')
                print('Toss something in there and try again!')
                continue
            valid_answer = False
            codex_tokens = 0
            while valid_answer == False:
                user_input = ''
                user_input = input('Make sure you have a codex_prompt.txt file in the filepath! Set max codex tokens: ')
                try:
                    user_input = int(user_input)
                    if (0 < user_input) and (user_input <= 1000):
                        codex_tokens = user_input
                        valid_answer = True
                    else:
                        print(f'Choose a value under {max_codex}')
                except:
                    print(f'Format should be a valid integer less than {max_codex}')

            try:
                codex_prompt = read_codex_prompt()
                
                response = generate_text(codex_prompt, engine, codex_tokens)[0]['text']
                full_log += response
                print(response)
                with open(f'{filepath}/codex_response.txt', 'w') as file:
                    file.write(response)
            except:
                print('Response not generated. See above error.')
                replace_input = True
                replace_input_text = 'quit'
                continue
        else:
            if debug: print('beep')
            try:
                response = generate_text(history + prompt, engine, max_tokens)[0]['text']
            except:
                print('Response not generated. See above error.')
                replace_input = True
                replace_input_text = 'quit'
                continue
            if debug: print('beep')
            if response:
                if debug: print('beep')
                time_taken = time.time()-start
                #add a delimiter to distinguish from user text
                response_delimiter = f'(*{round(time_taken, 1)}s)'
                cached_history = history
                history += prompt + response + '\n'
                full_log += f'({response_count+1}.)' + prompt + '\n' + response_delimiter + response + '\n'
                prompt_token_count += token_count(prompt)
                response_token_count += token_count(response)
                print(f'Response {response_count+1}: {response}\n\n')
                response_count += 1
                print(f'response time: {round(time_taken, 1)} seconds')
                correlation_log.append((time_taken, response_token_count))
                continue
            else:
                full_log += '*x*'
                print('*x*')
                if debug: print('beep')
                continue

def main():
    
    slow_status = False

    # slow_status = False defaults to davinci - True defaults to curie + disables davinci
    logs = interactive_chat(slow_status, max_tokens)
    if logs:
        (convo, correlates, logging_on) = logs
        if logging_on:
            write_to_log_file(convo, correlates)
        else:
            print('This conversation was not logged. Have a nice day.')
    else:
        print('Error. Cannot set convo and correlates logfiles.')
        return
    
if __name__ == '__main__':
    main()


