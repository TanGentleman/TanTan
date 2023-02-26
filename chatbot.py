import openai
import sys
import datetime
import time
from os import path
import config as c
TanSaysNoNo = c.TanEx

openai_key = c.get_openai_api_key()

filepath = f'{c.filepath}/Chatbot'
full_logfile = 'logfile.txt'
response_time_logfile = 'response_time_log.txt'

default_engine = 'text-davinci-003'
default_slow_engine = 'text-curie-001'

default_max_tokens = 300
max_tokens = default_max_tokens

# You can increase the following values after playing around a bit
max_codex = 4000
max_token_limit = 2000
max_session_total_tokens = 4000
warning_history_count = 1500

# These will be configurable variables in future updates. Presets need to be added first.
temperature = 0
frequency_penalty_val = None

# BETA
conversation_preset = True

slow_status = False # slow_status = False defaults to davinci - True defaults to curie + disables davinci
debug = False

def quit_chat(replace_input, replace_input_text):
    replace_input = True
    replace_input_text = 'quit'
    return replace_input, replace_input_text

def token_count(s:str):
    return len(s.strip().split(' '))

def check_truncation_and_toks(response):
    completion_tokens, prompt_tokens, total_tokens = (0,0,0)
    usage_vals = ['completion_tokens', 'prompt_tokens', 'total_tokens']
    # Check for other potential issues here
    for i in range(len(usage_vals)):
        try:
            tok_val = response['usage'][usage_vals[i]]
            if i == 0: completion_tokens = tok_val
            elif i == 1: prompt_tokens = tok_val
            elif i == 2: total_tokens = tok_val
        except:
            print(f'Token value not found for {usage_vals[i]}')
    try:
        response = response['choices'][0]
    except:
        print("Could not access response['choices']")
        raise(TanSaysNoNo)

    if response['finish_reason'] == 'length':
        print('*Warning: message may be truncated. Adjust max tokens as needed.')
    return response['text'], completion_tokens, prompt_tokens, total_tokens

def response_worked(response_input_vars):
    (previous_history, debug, full_log, history, prompt, response, response_count, time_taken) = response_input_vars
    if debug: print('beep, response worked')
    #add a marker to distinguish from user text
    response_time_marker = f'(*{round(time_taken, 1)}s)'
    previous_history = history
    history += prompt + response
    if token_count(history) > warning_history_count:
        print(f'Conversation token count is growing large [{token_count(history)}]. Please reset my memory as needed.')
    full_log += f'({response_count+1}.)' + prompt + '\n' + response_time_marker + response + '\n'
    print(f'Response {response_count+1}: {response}\n\n')
    response_count += 1
    print(f'response time: {round(time_taken, 1)} seconds')
    response_output_vars = (previous_history, full_log, history, response_count)
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

def read_download_prompt():
    try:
        contents_path = f'{filepath}/download_template.txt'
        with open(contents_path, 'r') as file:
            file_contents = file.read()
            return file_contents
    except FileNotFoundError:
        print('No download_template.txt in this directory found')



def generate_text(debug, prompt, engine, max_tokens):
    # Set the API key
    openai.api_key = openai_key
    
    # Generate responses using the model
    try:
       response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        max_tokens=max_tokens,
        temperature = 0 if 'code' in engine else temperature
        )
        
    except openai.error.OpenAIError as e:
        status = e.http_status
        error_dict = e.error
        
        print(status)
        print(error_dict)
        print(type(status), type(error_dict))
        if status == 400:
            if error_dict['type'] == 'invalid_request_error':
                message = error_dict['message']
                print(f'invalid_request_error: {message}')
        return
    if debug: print(response)
    return response


def write_to_log_file(convo, response_times):
    try:
        with open(f'{filepath}/{full_logfile}', 'a') as file:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d')
            file.write(f'Timestamp: {timestamp}\n{convo}\n ==== End of Entry ====\n')
            print('Saved conversation log file.')
        with open(f'{filepath}/{response_time_logfile}', 'a') as file:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d')
            file.write(f'Timestamp: {timestamp}\n{response_times}\n ==== End of Entry ====\n')
            print('Saved response time log file.')
    except:
        print('error. Unable to find path to logfile.')


def parse_args(args, slow_status, engine, max_tokens, debug):
    """
    This function parses the command line arguments and returns the engine, max_tokens, and debug values.
    """

    if args == []: # No arguments provided, return default values
        return engine, max_tokens, debug
    arg_count = len(args)
    # '-d' argument given to toggle debug mode on/off
    if '-d' in args: 
        debug = not(debug) # Toggle debugging state
        print(f'debug set to {debug}')
        args.remove('d')
        arg_count-=1
    # This code needs to become friendlier, but it works for now
    for i in range(arg_count):
        if args[i] == 'config': # If the config argument is given
            try:
                test_engine = args[i+1] # Get the engine name
                try:
                    test_engine = engine_choice(test_engine, slow_status) # Check if the engine is valid
                    engine = test_engine # Set the engine to the new value
                    ask_engine = False # Don't ask for the engine again
                    try:
                        test_toks = int(args[i+2]) # Get the max tokens value
                        temp_tok_limit = 0
                        if engine == 'code-davinci-002':
                            temp_tok_limit = max_codex # Set the max tokens limit to the codex limit
                        else:
                            temp_tok_limit = max_token_limit # Set the max tokens limit to the normal limit

                        if (test_toks > 0) and (test_toks <= temp_tok_limit):
                            max_tokens = test_toks # Set the max tokens to the new value
                            ask_token = False # Don't ask for the max tokens again
                            engine, max_tokens = configurate(ask_engine, ask_token, slow_status, engine, max_tokens) # Configurate the engine and max tokens
                            return engine, max_tokens, debug
                        else:
                            print(f'Max tokens value must be under {temp_tok_limit}.') # Print an error message
                            ask_token = True # Ask for the max tokens again
                            engine, max_tokens = configurate(ask_engine, ask_token, slow_status, engine, max_tokens) # Configurate the engine and max tokens
                            break
                    except NameError:
                        ask_engine = True # Ask for the engine again
                        ask_token = True # Ask for the max tokens again
                        break
                    except IndexError: # If no input arg for tokens
                        ask_token = True # Ask for the max tokens again
                        engine, max_tokens = configurate(ask_engine, ask_token, slow_status, engine, max_tokens) # Configurate the engine and max tokens
                    except ValueError: # If the max tokens value is not an integer
                        print('Integers only!') # Print an error message
                        ask_token = True # Ask for the max tokens again
                        engine, max_tokens = configurate(ask_engine, ask_token, slow_status, engine, max_tokens) # Configurate the engine and max tokens
                        break
                    except:
                        # I DONT THINK I CAN GET HERE BUT IDK
                        print('what got me here? Trace this') # Print an error message
                        assert(False)
                except NameError: # If the engine is not valid
                    ask_engine = True # Ask for the engine again
                    ask_token = True # Ask for the max tokens again
                    break
            except IndexError: # If no input arg for engine
                ask_engine = True # Ask for the engine again
                ask_token = True # Ask for the max tokens again
                break
    return engine, max_tokens, debug


def engine_choice(engine_prompt, slow_status):
    if len(engine_prompt) < 2:
        print('Please enter at least two characters')
        raise(NameError)
    if (engine_prompt == 'text-ada-001') or ('ada'.startswith(engine_prompt)):
        engine = 'text-ada-001'
        return engine
    elif (engine_prompt == 'text-babbage-001') or ('babbage'.startswith(engine_prompt)):
        engine = 'text-babbage-001'
        return engine
    elif (engine_prompt == 'text-curie-001') or ('curie'.startswith(engine_prompt)):
        engine = 'text-curie-001'
        return engine

    elif (engine_prompt == 'code-davinci-002') or ('codex'.startswith(engine_prompt)):
        if slow_status == True:
            print('Codex unavailable, switching to curie.')
            engine = 'text-curie-001'
            return engine
        else:
            engine = 'code-davinci-002'
            return engine
    elif (engine_prompt == 'text-davinci-003') or ('davinci'.startswith(engine_prompt)):
        if slow_status == True:
            print('Davinci unavailable, switching to curie.')
            engine = 'text-curie-001'
            return engine
        else:
            engine = 'text-davinci-003'
            return engine
    else:
        print('invalid')
        raise(NameError)

def set_max_tokens(max_tokens):
    legal_answer = False
    while legal_answer == False:
        token_prompt = input('Max Token count: ')
        if input in ['', ' ']:
            token_prompt = default_max_tokens
            print(f'Max tokens [default]: {default_max_tokens}')
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
    else:
        try:
            engine = engine_choice(engine, slow_status)
        except:
            print('Welp, dunno how it broke. Help?')
    if ask_token:
        max_tokens = set_max_tokens(max_tokens)
    
    return engine, max_tokens

def choosePreset(n):
    if n == 1:
        prompt_prelude = '''Human: Hello, how are you?
AI: I am doing great. How can I help you today?
Human:'''
        prefix = '\nHuman: '
        suffix = '\nAI: '

# This function needs proper re-structuring for readability!
def interactive_chat(slow_status, engine, max_tokens, debug):
    completion_tokens, prompt_tokens, total_tokens, session_total_tokens = (0, 0, 0, 0)
    history, previous_history, full_log = ('', '', '')
    response_count = 0
    response_time_log = []
    logging_on = True
    prompt_from_file = False
    config_info = f'Engine set to: {engine}, {max_tokens} Max Tokens\n'
    full_log += config_info
    print(config_info)
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

        # ESCAPE COMMAND
        if prompt == 'quit':
            if session_total_tokens == 0:
                logging_on = False
                print('This was not logged.')
            else:
                full_log += f'tokens used: {session_total_tokens}'
            return full_log, response_time_log, logging_on

        elif prompt == None:
            print('Type a lil somethin at least')
        elif prompt == 'stats':
            print(f'engine: {engine}, max_tokens = {max_tokens}, tokens used: {session_total_tokens}')
        elif prompt.startswith('config'):
            if prompt in ['config', 'config -d']:
                if '-d' in prompt:
                    debug = not(debug)
                    print(f'Debug set to {debug}')
                ask_engine = True
                ask_token = True
                engine, max_tokens = configurate(ask_engine, ask_token, slow_status, engine, max_tokens)
                msg = f'Engine set to: {engine}, {max_tokens} Max Tokens'
            else:
                args = prompt.split(' ')
                args_count = len(args)
                if args_count > 4:
                    print('Did you mean to type a config command? Format is "config [engine] [tokens] [-d]" ')
                    continue
                else:
                    engine, max_tokens, debug = parse_args(args, slow_status, engine, max_tokens, debug)
            msg = f'Engine set to: {engine}, {max_tokens} Max Tokens'
            print(msg + '\n')
            full_log += msg + '\n'
            continue

        elif prompt == 'help':
            print('Available commands: codex, del, forget, help, history, log, read, stats, (tok or token),  config, config [engine] [tokens] [-d:optional]')
        elif prompt == 'history':
            if history:
                print(f'HISTORY shown below:\n\n{(history)}')
            else:
                print('No conversation history in memory.')
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
                print('Reading text_prompt.txt')
                prompt_from_file = True
                replace_input = True
                continue
            else:
                print('You have not written a text_prompt.txt file for me to read. I gotchu.')
                with open(f'{filepath}/text_prompt.txt', 'w') as file:
                    file.write('Insert text prompt here')
            continue

            # Codex takes the input from codex_prompt.txt and completes the given task. It does not use past conversation history,
        elif prompt == 'codex':
            print(f'Trying codex!')
            if path.isfile(f'{filepath}/codex_prompt.txt'):
                pass
            else:
                print('You have not written a codex_prompt.txt file for me to read. I gotchu.')
                try:
                    with open(f'{filepath}/codex_prompt.txt', 'w') as file:
                        file.write('Please create the following function with comments in Python:\n' +
                                        'def myFunc():\n\t#Do THIS\nSeed Text: It should be optimized for performance and readability.')
                except:
                    print(f'Error! Could not write to {filepath}/codex_prompt.txt')
                print('Toss something in there and try again!')
                continue
            valid_answer = False
            codex_tokens = 0
            while valid_answer == False:
                user_input = ''
                user_input = input('Make sure you have a codex_prompt.txt file in the filepath! Set max codex tokens: ')
                try:
                    # if user_input == 'quit':
                    #     replace_input, replace_input_text = quit_chat()
                    #     continue
                    user_input = int(user_input)
                    if (0 < user_input) and (user_input <= max_codex):
                        codex_tokens = user_input
                        valid_answer = True
                    else:
                        print(f'Choose a value under {max_codex}')
                except:
                    print(f'Format should be a valid integer less than {max_codex}')

            try: #1
                codex_prompt = read_codex_prompt()
                try: #2
                    response = generate_text(debug, codex_prompt, 'code-davinci-002', codex_tokens)
                except:
                    print('Codex response not generated. Error 2.')
                    continue
                try: #3
                    response, completion_tokens, prompt_tokens, total_tokens = check_truncation_and_toks(response)
                except:
                    print('Codex response not generated. Error 3.')
                    continue
                if response:
                    try: #4
                        time_taken = time.time()-start_time
                        response_input_vars = (previous_history, debug, full_log, history, prompt, response, response_count, time_taken)
                        response_output_vars = response_worked(response_input_vars)
                        response_time_log.append((time_taken, total_tokens, engine))
                        (previous_history, full_log, history, response_count) = response_output_vars
                    except:
                        print('Codex response not generated. Error 4.')
                else:
                    print('Blocked or truncated')
                    full_log += '*x*'
                    continue
                try:
                    with open(f'{filepath}/codex_response.txt', 'w') as file:
                        file.write(response)
                        print('Saved codex_response.txt')
                except:
                    print('Could not save codex_response.txt')
                    
                session_total_tokens += total_tokens
                if session_total_tokens > max_session_total_tokens:
                    print('CONVO GETTIN LONG')
                continue
            except:
                print('Codex response not generated. Error 1.')
                continue

        elif prompt in ['tok', 'token']:
            max_tokens = set_max_tokens(max_tokens)
        else:
            # All valid non-command inputs to the bot go through here.
            if conversation_preset and prompt == 'download':
                raw_input = input('Throw something at me. Magic string headed back your way:\n')
                try:
                    template = read_download_prompt()
                except:
                    print('welp, could not read download_template.txt')
                    continue
                prompt = template + raw_input + '\nOutput:'
                history = ''
                max_tokens = 10
            if debug: print('beep, about to try generating response')
            try:
                # Continues the conversation (Doesn't add newline if no history)
                response = generate_text(debug, history + '\n' + prompt if history else prompt, engine, max_tokens)
            except:
                print('Response not generated. See above error. Try again?')
                continue
            response, completion_tokens, prompt_tokens, total_tokens = check_truncation_and_toks(response)
            if debug: print('beep')
            if response:
                time_taken = time.time()-start_time
                response_input_vars = (previous_history, debug, full_log, history, prompt, response, response_count, time_taken)
                response_output_vars = response_worked(response_input_vars)
                (previous_history, full_log, history, response_count) = response_output_vars
                session_total_tokens += total_tokens

                response_time_log.append((time_taken, total_tokens, engine))
                if session_total_tokens > max_session_total_tokens:
                    print('CONVERSATION TOO LONG')
                continue
            else:
                print('Blocked or truncated')
                full_log += '*x*'
                continue
def main(engine, max_tokens, debug):
    if openai_key == None:
        print('Please set your OpenAI key in config.py')
        return
    logs = interactive_chat(slow_status, engine, max_tokens, debug)
    if logs:
        (convo, response_times, logging_on) = logs
        if logging_on:
            write_to_log_file(convo, response_times)
        else:
            print('This conversation was not logged. Have a nice day.')
    else:
        print('Error. Cannot set conversation and response time logfiles.')
        return

def get_args(args):
    if slow_status == True: 
        engine = default_slow_engine
    else:
        engine = default_engine

    max_tokens = default_max_tokens
   
    arg_count = len(args)
    if '-d' in args:
        args.remove('-d')
        arg_count -= 1
        debug = True
        print('Debug set to True')
    else:
        debug = False
    
    if arg_count > 1:
        engine, max_tokens, debug = parse_args(args, slow_status, engine, max_tokens, debug)

    return engine, max_tokens, debug

# Default script execution from CLI, uses sys.argv arguments
if __name__ == '__main__':
    import sys
    args = sys.argv
    engine, max_tokens, debug = get_args(args)
    main(engine, max_tokens, debug)

# Manual function execution from python environment with `import chatbot`, uses a given argument list
def py_env_main(args):
    engine, max_tokens, debug = get_args(args)
    main(engine, max_tokens, debug)
