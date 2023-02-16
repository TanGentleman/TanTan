import openai
from mysecrets import openai_key
import sys
import datetime
import time
from os import path

filepath = 'Documents/Github/Api_Mastery/Chatbot'
full_logfile = 'v3_logfile.txt'
response_time_logfile = 'v3_response_time_log.txt'


default_max_tokens = 100
max_codex = 1000
max_token_limit = 1000
max_tokens = default_max_tokens
slow_status = False

def quit_chat(replace_input, replace_input_text):
    replace_input = True
    replace_input_text = 'quit'
    return replace_input, replace_input_text

def token_count(s:str):
    return len(s.strip().split(' '))

def check_truncation_and_toks(response, completion_tokens, prompt_tokens, total_tokens):
    usage_vals = ["completion_tokens", "prompt_tokens", "total_tokens"]
    for i in range(len(usage_vals)):
        try:
            tok_val = response["usage"][usage_vals[i]]
            if i == 0: completion_tokens = tok_val
            elif i == 1: prompt_tokens = tok_val
            elif i == 2: total_tokens = tok_val
        except:
            print(f"Token value not found for {usage_vals[i]}")
    response = response["choices"][0]

    if response["finish_reason"] == 'length':
        print("*Warning: message may be truncated. Adjust max tokens as needed.")
    return response["text"], completion_tokens, prompt_tokens, total_tokens

def response_worked(response_input_vars):
    (previous_history, response_time_log, debug, full_log, history, prompt, response, response_count, start_time, total_tokens) = response_input_vars
    if debug: print('beep, response worked')
    time_taken = time.time()-start_time
    #add a delimiter to distinguish from user text
    response_delimiter = f'(*{round(time_taken, 1)}s)'
    previous_history = history
    history += prompt + response + '\n'
    if token_count(history) > 500:
        print(f"Conversation token count is growing large [{token_count(history)}]. Please reset my memory as needed.")
    full_log += f'({response_count+1}.)' + prompt + '\n' + response_delimiter + response + '\n'
    print(f'Response {response_count+1}: {response}\n\n')
    response_count += 1
    print(f'response time: {round(time_taken, 1)} seconds')
    response_time_log.append((time_taken, total_tokens))
    response_output_vars = (previous_history, response_time_log, full_log, history, response_count)
    return response_output_vars
        
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



def generate_text(debug, prompt, engine, max_tokens):
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
        status = e.http_status
        error_dict = e.error
        
        print(e.http_status)
        print(e.error)
        print(type(status), type(error_dict))
        if status == 400:
            if error_dict['type'] == 'invalid_request_error':
                message = error_dict['message']
                print(f'Keeper: {message}')
        return
    if debug: print(response)
    return response

def write_to_log_file(convo, response_times):
    with open(f'{filepath}/{full_logfile}', 'a') as file:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d')
        file.write(f'Timestamp: {timestamp}\n{convo}\n ==== End of Entry ====\n')
        print('Saved log file.')
    with open(f'{filepath}/{response_time_logfile}', 'a') as file:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d')
        file.write(f'Timestamp: {timestamp}\n{response_times}\n ==== End of Entry ====\n')
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

def set_max_tokens(max_tokens):
    legal_answer = False
    while legal_answer == False:
        token_prompt = input('Max Token count: ')
        if input in ['', ' ']:
            token_prompt = default_max_tokens
        try:
            token_prompt = int(token_prompt)
            if (token_prompt > 0) and (token_prompt <= max_token_limit):
                max_tokens = token_prompt
                legal_answer = True
            else:
                print(f'Try a value between 1 and {max_token_limit} for now')
        except:
            print(f'Not recognized max token value. Try an integer from 1 to {max_token_limit}.')
    return max_tokens

def configurate(ask_engine, ask_token, slow_status, engine, max_tokens):
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
        max_tokens = set_max_tokens(max_tokens)
    return engine, max_tokens

def interactive_chat(slow_status, max_tokens):
    (completion_tokens, prompt_tokens, total_tokens, session_total_tokens) = (0, 0, 0, 0)
    (history, previous_history, full_log) = ('', '', '')
    response_count = 0
    response_time_log = []
    debug = False
    logging_on = True
    prompt_from_file = False
    if slow_status == True:
        engine = 'text-curie-001'
    else:
        engine = 'text-davinci-003'
        
    config_args = parse_args()
    if config_args: 
        (ask_engine, ask_token, debug) = config_args
        if debug: print('beep')
        engine, max_tokens = configurate(ask_engine, ask_token, slow_status, engine, max_tokens)
    config_info = f'Engine set to: {engine}, {max_tokens} Max Tokens\n'
    full_log += config_info
    if debug: print(config_info)
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
        start_time = time.time()

        #if it works

        # ESCAPE COMMAND
        if prompt == 'quit':
            print(f'tokens used: {session_total_tokens}')
            full_log += f'tokens used: {session_total_tokens}'
            return full_log, response_time_log, logging_on

        elif prompt in ['', ' ']:
            print('Type a lil somethin at least')
        elif prompt == 'stats':
            print(f'engine: {engine}, max_tokens = {max_tokens}, tokens used: {session_total_tokens}')
        elif prompt in ['config', 'config -d']:
            engine, max_tokens = configurate(True, True, slow_status, engine, max_tokens)
            msg = f'Engine set to: {engine}, {max_tokens} Max Tokens'
            if '-d' in prompt:
                debug = not(debug)
                msg = msg + f', debug set to {debug}'
            print(msg + '\n')
            full_log += msg + '\n'
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
            history = previous_history
            msg = '<I have deleted the last exchange from my memory>\n'
            print(msg)
            full_log += msg
        elif prompt == 'log':
            
            if logging_on:
                msg = '<Logging disabled> Conversation will not be stored.\n'
                print(msg)
                logging_on = False
            else:
                msg = '<Logging enabled> Conversation WILL be stored.\n'
                print(msg)
                logging_on = True
        elif prompt == 'read':
            if path.isfile(f'{filepath}/text_prompt.txt'):
                text_prompt = read_text_prompt()
                prompt_from_file = True
                replace_input = True
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
                    if user_input == 'quit':
                        replace_input, replace_input_text = quit_chat()
                        continue
                    user_input = int(user_input)
                    if (0 < user_input) and (user_input <= max_codex):
                        codex_tokens = user_input
                        valid_answer = True
                    else:
                        print(f'Choose a value under {max_codex}')
                except:
                    print(f'Format should be a valid integer less than {max_codex}')

            try:
                codex_prompt = read_codex_prompt()
                try:
                    response = generate_text(debug, codex_prompt, engine, codex_tokens)
                except:
                    print('Response not generated. See above error. Try again?')
                    continue
                response, completion_tokens, prompt_tokens, total_tokens = check_truncation_and_toks(response, completion_tokens, prompt_tokens, total_tokens)
                if response:
                    response_input_vars = (previous_history, response_time_log, debug, full_log, history, prompt, response, response_count, start_time, total_tokens)
                    response_output_vars = response_worked(response_input_vars)
                    (previous_history, response_time_log, full_log, history, response_count) = response_output_vars
                else:
                    print("Blocked or truncated")
                    full_log += '*x*'
                    continue

                with open(f'{filepath}/codex_response.txt', 'w') as file:
                    file.write(response)
                    print('Saved codex_response.txt')
                session_total_tokens += total_tokens
                continue
            except:
                print('Response not generated. See above error. Try again?')
                continue

        elif prompt in ['tok', 'token']:
            max_tokens = set_max_tokens(max_tokens)
        else:
            # All valid non-command inputs to the bot go through here.
            if debug: print('beep')
            try:
                response = generate_text(debug, history + prompt, engine, max_tokens)
            except:
                print('Response not generated. See above error. Try again?')
                continue
            response, completion_tokens, prompt_tokens, total_tokens = check_truncation_and_toks(response, completion_tokens, prompt_tokens, total_tokens)
            if debug: print('beep')
            if response:
                    response_input_vars = (previous_history, response_time_log, debug, full_log, history, prompt, response, response_count, start_time, total_tokens)
                    response_output_vars = response_worked(response_input_vars)
                    (previous_history, response_time_log, full_log, history, response_count) = response_output_vars
                    session_total_tokens += total_tokens
                    continue
            else:
                print("Blocked or truncated")
                full_log += '*x*'
                continue
def main():
    max_tokens = default_max_tokens
    # slow_status = False defaults to davinci - True defaults to curie + disables davinci
    logs = interactive_chat(slow_status, max_tokens)
    if logs:
        (convo, response_times, logging_on) = logs
        if logging_on:
            write_to_log_file(convo, response_times)
        else:
            print('This conversation was not logged. Have a nice day.')
    else:
        print('Error. Cannot set conversation and response time logfiles.')
        return
    
if __name__ == '__main__':
    main()


