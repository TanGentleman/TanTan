import openai
import sys
import datetime
import time
from os import path
import config as c
import clipboard
if c.dev:
    from os import environ
    from transformers import GPT2TokenizerFast
    tokenize = GPT2TokenizerFast.from_pretrained("gpt2", local_files_only = True).tokenize
    environ["TOKENIZERS_PARALLELISM"] = "false"
    import image_generation as ig
    dev = True
else:
    dev = False
TanSaysNoNo = c.TanEx

openai_key = c.get_openai_api_key()
filepath = f'{c.filepath}/Chatbot'
full_logfile = 'logfile.txt'
response_time_logfile = 'response_time_log.txt'

slow_status = False # slow_status = False defaults to davinci - True defaults to curie + disables davinci
default_engine = 'text-davinci-003'
default_slow_engine = 'text-curie-001'

default_max_tokens = 300
max_tokens = default_max_tokens

# You can increase the following values after playing around a bit
max_codex = 4000
max_token_limit = 4000
max_session_total_tokens = 4000
warning_history_count = 3000

# These will be configurable variables in future updates. Presets need to be added first.
default_temperature = 0.3
frequency_penalty_val = 1.0


debug = False

cmd_dict = {
            'config': 'Prompts configuration of engine and max_tokens. `config [engine] [tokens] [-d]`',
            'codex': 'Generate code from codex_prompt.txt',
            'debug': 'Toggle debug mode. Alias -d',
            'del': 'Delete the last exchange from memory',
            'forget': 'Forget the past conversation. Alias -f',
            'help': 'Display the list of commands',
            'history': 'The current conversation in memory', 
            'log': 'Toggle to enable or disable logging of conversation + response times', 
            'read': 'Respond to text_prompt.txt', 
            'save': 'Save the current conversation log to conversation.txt. Alias -s',
            'stats': 'Prints the current configuration and session total tokens.',
            'tanman': 'brings up the TanManual (commands with their descriptions). Alias tan',
            'temp': 'Configure temperature (0.0-1.0)',
            'tok': 'Configure max tokens for the response',
            '-c': 'Respond to clipboard text (Uses conversation history)',
            '-cs': 'Summarize clipboard text (Amnesic)',
            '-r': 'Amnesic command, as lone command it uses clipboard contents as prompt\n' +
                    'To format: Replace second instance of -r with contents of clipboard:\n' + 
                    'Syntax: `-r [prefix text] -r [optional suffix text]`\n' +
                    'Example Usage: `-r Define this word: # -r #`\n' +
                    'Replaces prompt with: Define this word: #clipboard_contents#'
            }



def set_prompt(prompt, prefix = None,  suffix = None):
    if prefix is None:
        prefix = ''
    if suffix is None:
        suffix = ''
    prompt = prefix + prompt + suffix
    return prompt

# Needs comments and clearer error handling after response fails
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
            print('Response failed.')
            raise(TanSaysNoNo)
    try:
        response = response['choices'][0]
    except:
        print("Could not access response['choices']")
        raise(TanSaysNoNo)

    if response['finish_reason'] == 'length':
        print('*Warning: message may be truncated. Adjust max tokens as needed.')
    return response['text'], completion_tokens, prompt_tokens, total_tokens

def read_prompt(filepath, filename):
    try:
        contents_path = f'{filepath}/{filename}'
        with open(contents_path, 'r') as file:
            file_contents = file.read()
            return file_contents
    except FileNotFoundError:
        print(f'No {filename} in this directory found')

def read_codex_prompt():
    filename = 'codex_prompt.txt'
    text = read_prompt(filepath, filename)
    if text:
        return text
    else:
        print('Could not read codex_prompt.txt')

def read_text_prompt():
    filename = 'text_prompt.txt'
    text = read_prompt(filepath, filename)
    if text:
        return text
    else:
        print(f'Could not read {filename}')

def read_download_template():
    filename = 'TrainingData/download_template.txt'
    text = read_prompt(filepath, filename)
    if text:
        return text
    else:
        print(f'Could not read {filename}')


# Needs comments
def generate_text(debug, prompt, engine, max_tokens, temperature):
    # Set the API key
    openai.api_key = openai_key
    
    # Generate responses using the model
    try:
       response = openai.Completion.create(
        engine=engine,
        prompt=prompt,
        # testing this 2000 thing for a sec
        max_tokens = 2000 if (max_tokens > 2000 and 'davinci' not in engine) else max_tokens,
        temperature = 0 if 'code' in engine else temperature,
        frequency_penalty = frequency_penalty_val,
        stop = '*stop*'
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

# In development
def try_gen(size):
    valid = False
    while valid == False:
        try:
            ig.generate_images_from_prompts(size)
            valid = True
        except:
            print('Image generation failed.')
            return
    print('Image generation successful!')
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
    '''
    This function parses the command line arguments and returns the engine, max_tokens, and debug values.
    '''

    if args == []: # No arguments provided, return default values
        return engine, max_tokens, debug
    arg_count = len(args)
    # '-d' argument given to toggle debug mode on/off
    if '-d' in args: 
        debug = not(debug) # Toggle debugging state
        print(f'debug set to {debug}')
        args.remove('-d')
        arg_count-=1
    # This code needs to become friendlier, but it works for now
    for i in range(arg_count):
        if args[i] == 'config': # If the config argument is given
            try:
                test_engine = args[i+1] # Get the engine name
            except IndexError: # If no input arg for engine
                ask_engine = True # Ask for the engine again
                ask_token = True # Ask for the max tokens again
                engine, max_tokens = configurate(ask_engine, ask_token, slow_status, engine, max_tokens) # Configurate the engine and max tokens
                break
            try:
                test_engine = engine_choice(test_engine, slow_status) # Check if the engine is valid
            except NameError: # If the engine is not valid
                ask_engine = True # Ask for the engine again
                ask_token = True # Ask for the max tokens again
                engine, max_tokens = configurate(ask_engine, ask_token, slow_status, engine, max_tokens) # Configurate the engine and max tokens
                break
            engine = test_engine # Set the engine to the new value
            ask_engine = False # Don't ask for the engine again
            try:
                test_toks = int(args[i+2]) # Get the max tokens value
            except ValueError: # If the max tokens value is not an integer
                print('Integers only!') # Print an error message
                ask_token = True # Ask for the max tokens again
                engine, max_tokens = configurate(ask_engine, ask_token, slow_status, engine, max_tokens) # Configurate the engine and max tokens
                break
            except IndexError: # If no input arg for tokens
                # I CHANGED THIS
                ask_token = False # Do NOT Ask for the max tokens again
                engine, max_tokens = configurate(ask_engine, ask_token, slow_status, engine, max_tokens) # Configurate the engine and max tokens
                break
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
        else:
            if i == 0:
                continue
            print(f'Invalid argument on {args[i]}. Syntax is config (engine) (max_tokens) (optional -d)')
            ask_engine = True # Ask for the engine again
            ask_token = True # Ask for the max tokens again
            engine, max_tokens = configurate(ask_engine, ask_token, slow_status, engine, max_tokens) # Configurate the engine and max tokens
            break
    return engine, max_tokens, debug

def engine_choice(engine_prompt, slow_status):
    if len(engine_prompt) < 2:
        print('Please enter at least two characters for the engine selection.')
        raise(NameError)
    elif (engine_prompt == 'text-ada-001') or ('ada'.startswith(engine_prompt)):
        engine = 'text-ada-001'
        return engine
    elif (engine_prompt == 'text-embedding-ada-002') or ('adae'.startswith(engine_prompt)):
        engine = 'text-embedding-ada-002'
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
        print('invalid engine choice')
        raise(NameError)

# This function assumes both the default tokens and token limit are SAFE and correct values
def set_max_tokens(default, limit):
    # Keep trying until a valid max_tokens value is set
    legal_answer = False
    while legal_answer == False:
        user_input = input('Max Token count: ')
        if user_input in ['', ' ']:
            if default:
                print(f'Max tokens [default]: {default}')
                return default
            else:
                'You really like Blank Space, huh?'
                continue
        try:
            user_tokens = int(user_input)
        except:
            print(f'Not recognized max token value. Try an integer from 1 to {limit}.')
            continue

        if (user_tokens > 0) and (user_tokens <= limit):
            max_tokens = user_tokens
            legal_answer = True
        else:
            print(f'Try a value between 1 and {limit} for now')
    # Answer is legal, return it
    return max_tokens

# This function assumes both the default tokens and token limit are SAFE and correct values
def set_temperature(default):
    legal_answer = False
    while legal_answer == False:
        user_input = input('Temperature: ')
        if user_input in ['', ' ']:
            print(f'Temperature [default]: {default}')
            return default
        try:
            user_temp = float(user_input)
        except:
            print('Not recognized temp value. Try a float from 0.0 to 1.0.')
            continue

        if (user_temp >= 0.0) and (user_temp <= 1.0):
            temperature = user_temp
            legal_answer = True
        else:
            print('Try a value between 0.0 and 1.0')
    return round(temperature,2)

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
            print('config():Welp, seems your engine appears invalid to engine_choice(). I shall leave it alone.')
    if ask_token:
        default = default_max_tokens
        limit = max_token_limit
        max_tokens = set_max_tokens(default, limit)
    return engine, max_tokens


# This function needs proper re-structuring for readability!
def interactive_chat(slow_status:bool, engine:str, max_tokens:int, debug:bool):
    completion_tokens, prompt_tokens, total_tokens, session_total_tokens = (0, 0, 0, 0)
    history, previous_history,  = ('', '')
    
    full_log, response_time_log = ('','')
    logging_on = True
    replace_input = False
    replace_input_text = ''
    

    amnesia = False
    cached_engine = None
    cached_history = None
    cached_tokens = None
    

    response_count = 0
    chat_ongoing = True

    temperature = default_temperature
    config_info = f'Engine: {engine}, {max_tokens} Max Tokens, Temp is {temperature}\n'
    full_log += config_info
    print(config_info)
    while chat_ongoing:
        # Amnesia mode saves current configuration and history for next prompt
        if amnesia:
            amnesia = False
        else:
            # The following 3 assume correctness of cached vars
            if cached_engine:
                engine = cached_engine # Restore the engine
                cached_engine = None
            if cached_history:
                history = cached_history # Restore the history
                cached_history = None
            if cached_tokens:
                max_tokens = cached_tokens # Restore the max_tokens
                cached_tokens = None

        # Get prompt
        if replace_input:
            prompt = replace_input_text # Use the replacement text
            replace_input = False
        else:
            prompt = input('Enter a prompt: ')

        # Start the timer
        start_time = time.time()

        # If Blank Space
        if len(prompt) < 1:
            print('Taylor Swift, I like it!')

        # Quit Chat
        elif prompt == 'quit':
            if session_total_tokens == 0:
                logging_on = False
                print('This was not logged.')
            else:
                full_log += f'Tokens used: {session_total_tokens}'
            # chat_ongoing = False (eventually will be updated)
            return full_log, response_time_log, logging_on

        # Need to organize the below commands
        elif prompt == 'stats':
            print(f'engine: {engine}, max_tokens = {max_tokens}, temp = {temperature}, tokens used: {session_total_tokens}')
        elif prompt in ['-d', 'debug']:
            debug = not(debug)
        elif prompt.startswith('config'):
            args = prompt.split(' ')
            args_count = len(args)
            if args_count > 4:
                print('Did you mean to type a config command? Format is: config [engine] [tokens] [-d]')
                continue
            else:
                engine, max_tokens, debug = parse_args(args, slow_status, engine, max_tokens, debug)
            msg = f'Engine set to: {engine}, {max_tokens} Max Tokens'
            print(msg + '\n')
            full_log += msg + '\n'
            continue
        # Embedded clipboard reading. Example command:-r Define this word: # -r #
        elif prompt.startswith('-r'): # Amnesic mode
            args = prompt.split(' ')
            args_count = len(args)
            if args_count == 1:
                if args[0] == '-r':
                    print('Reading clipboard. Working on response...')
                else:
                    print('Syntax for -r strings is `-r [prefix text] -r [optional suffix text]`')
                    continue
                replace_input = True
                replace_input_text = clipboard.paste()
                print('Reading clipboard. Working on response...')
                # Cache history here
                cached_history = history
                history = ''

                amnesia = True
                continue
            else:
                if '-r' not in args[1:]:
                    print('Format with a second -r, such as in: `-r Define this word: # -r #`')
                    continue
                else:
                    args = args[1:]
                    n = args.index('-r')
                    prefix = ' '.join(args[:n])
                    suffix = ' '.join(args[n+1:])
                    replace_input = True
                    replace_input_text = set_prompt(clipboard.paste(), prefix, suffix)
                    print('Reading clipboard and formatting. Working on response...')
            cached_history = history
            history = ''

            amnesia = True
            continue
        elif prompt == 'help': # Show list of commands
            print('For the full manual of commands and descriptions, type tan')
            text = ''
            # for i in range(len(cmd_dict)):
            #     text += f'{list(cmd_dict.keys())[i]}'
            print(list(cmd_dict.keys()))
        elif prompt == 'history': # Show convo history
            if history:
                print(f'Conversation in memory shown below:\n\n{(history)}')
            else:
                print('No conversation history in memory.')
        elif prompt in ['-f','forget']: # Erase convo history
            history = ''
            msg = '<History has been erased. Please continue the conversation fresh :)>\n'
            print(msg)
            full_log += msg
        elif prompt == 'del': # Delete last exchange
            if history == previous_history:
                print('No previous exchange to delete.')
                continue
            history = previous_history
            msg = '<I have deleted the last exchange from my memory>\n'
            print(msg)
            full_log += msg
        elif prompt == 'log': # Toggle logging
            if logging_on:
                msg = '<Logging disabled> Conversation will not be stored.\n'
                print(msg)
                logging_on = False
            else:
                msg = '<Logging enabled> Conversation WILL be stored.\n'
                print(msg)
                logging_on = True
        elif prompt == 'read': # Responds to text_prompt.txt
            # Amnesic reading
            if path.isfile(f'{filepath}/text_prompt.txt'):
                text_prompt = read_text_prompt()
                if text_prompt:
                    print('Reading text_prompt.txt')
                    replace_input = True
                    replace_input_text = text_prompt
                    cached_history = history
                    history = ''

                    amnesia = True
                    continue
                else:
                    print('text_prompt.txt is empty. Try adding something!')
            else:
                print('You have not written a text_prompt.txt file for me to read. I gotchu.')
                with open(f'{filepath}/text_prompt.txt', 'w') as file:
                    file.write('Insert text prompt here')
                print('Try adding something!')
        elif prompt == 'tok':
            default = max_tokens
            limit = max_token_limit
            max_tokens = set_max_tokens(default, limit)
        elif prompt == 'temp':
            temperature = set_temperature(temperature)
            print(f'Temperature set to {temperature}')
        elif prompt in ['-c','-cs']: 
            # -c is a NON-amnesic clipboard reader
            # -cs is an amnesic clipboard summarizer.

            # This is used to perform a completion using the text in one's clipboard. Check the below prompt framing.
            replace_input = True
            if prompt == '-cs': #clipboard summary? I think -cs kinda works
                prefix = '# Provide a brief summary of the following text:\n#'
                suffix = '\n#'
                replace_input_text = set_prompt(clipboard.paste(), 
                                prefix = 'Please provide a brief summary of the following text:\n#', suffix = '\n#')
                print('Summarizing clipboard text...')
                cached_history = history
                history = ''

                amnesia = True
                continue
            elif prompt == '-c':
                # I think I will keep this non-amnesic, as it may be useful to use -c to keep convo but with text selections.
                replace_input_text = clipboard.paste()
                print('Responding to clipboard text...')
                continue # No amnesia, so it will use the current history.

        elif prompt == 'codex':
            # Amnesic command, will not affect current configuration or history
            # Responds to codex_prompt.txt using codex engine
            
            # If file exists, read it. Else, write a template.
            if path.isfile(f'{filepath}/codex_prompt.txt'):
                print(f'Reading codex!')
            else:
                print('You have not written a codex_prompt.txt file for me to read. I gotchu.')
                with open(f'{filepath}/codex_prompt.txt', 'w') as file:
                        file.write('# This Python3 function [What it does]:\ndef myFunc():\n\t#Do THIS')
                        print('Toss something in there before setting the tokens!')
            
            # Set tokens (persistent until valid chosen!)
            default = None
            limit = max_codex
            codex_tokens = set_max_tokens(default, limit)
            
            # Set prompt
            codex_text = read_codex_prompt()

            if codex_text:
                # Replace prompt text with the text from codex_prompt.txt
                replace_input = True
                replace_input_text = codex_text

                # Cache history to continue conversation afterwards
                cached_history = history
                cached_engine = engine
                cached_tokens = max_tokens

                # Configure for codex, Bypasses slow_status!
                history = ''
                engine = 'code-davinci-002' # Latest codex model
                max_tokens = codex_tokens
                
                amnesia = True
                continue
            else:
                print('No readable text in codex_prompt.txt')
                continue
        elif prompt in ['tan', 'tanman']:
            
            text = '\nTanManual Opened! Available commands:\n\n' 
            for i in range(len(cmd_dict)):
                text += f'{list(cmd_dict.keys())[i]}: {list(cmd_dict.values())[i]}\n'
            print(text)      
        # This one is just experimentation for now
        # save the current full_log to a response.txt
        elif prompt in ['-s','save']:
            with open(f'{filepath}/conversation.txt', 'w') as file:
                file.write(full_log)
            print('Saved!')
        elif dev and prompt == 'download': 
            # image generation
            try_gen('default') 

            # Experimenting with a magic string generator for Link_Grabber.py to use

            # user_input = input('Throw something at me. Magic string headed back your way:\n')
            # template = read_download_template()
            # if template:
            #     replace_input = True
            #     prefix = template
            #     suffix = '\nOutput:'
            #     replace_input_text = set_prompt(user_input, prefix, suffix)
            #     history = ''
            #     max_tokens = 15
            #     cached_history = history
            #     history = ''

            #     amnesia = True
            #     continue
            # else:
            #     print('welp, could not read download_template.txt')
            #     continue
        else:
            # All valid non-command inputs to the bot go through here.
            if debug: print('beep, about to try generating response')
            if dev:
                tokenized_text = tokenize(prompt)
                token_count = len(tokenized_text)
                # This 4000 is a hard cap for the full completion. I'll work it in better soon. 
                if token_count + max_tokens > 4000:
                    print('WARNING: prompt is too long. I will try to generate a response, but it may be truncated.')
                    print(f'max_tokens would need to be set to roughly {4000-token_count}')
                print(f'prompt is {token_count} tokens')
            try:
                # Continues the conversation (Doesn't add newline if no history)
                response = generate_text(debug, history + '\n' + prompt if history else prompt, engine, max_tokens, temperature)
            except:
                print('Response not generated. See above error. Try again?')
                continue
            try:
                response, completion_tokens, prompt_tokens, total_tokens = check_truncation_and_toks(response)
            except:
                print('check_truncation_and_toks failure, fix incoming')
                continue
            if response:
                time_taken = time.time()-start_time
                if debug: print('beep, we got a response!')
                # Dev tokenization check
                if dev:
                    tokenized_text = tokenize(history)
                    token_count = len(tokenized_text)
                    if token_count > warning_history_count:
                        print(f'Conversation token count is growing large [{token_count}]. Please reset my memory as needed.')
                # Record a savestate and append history
                previous_history = history
                history += prompt + response + '\n'

                #add a marker to distinguish from user text
                RT = round(time_taken, 1)
                response_time_marker = f'(*{RT}s)' # (*1.2s) is the marker for 1.2 seconds
                engine_id = engine.split('-')
                engine_marker = engine_id[0][0] + engine_id[1][0] + engine_id[2][-1]
                response_count += 1
                # Log the response and response time
                full_log += f'({response_count}.)' + prompt + '\n' + response_time_marker + response + '\n'
                response_time_log += f'[#{response_count}, RT:{RT}, T:{total_tokens}, E:{engine_marker}]'

                # Print the response and response time
                print(f'Response {response_count}: {response}\n\n')
                print(f'response time: {round(time_taken, 1)} seconds')

                session_total_tokens += total_tokens
                
                if session_total_tokens > max_session_total_tokens:
                    print(f'Conversation is very lengthy. Session total tokens: {session_total_tokens}')
                if debug: print(f'This completion was {round(100*total_tokens/4096)}% of the davinci maximum')
                continue
            else:
                print('Blocked or truncated')
                full_log += '*x*'
                continue
def main(engine, max_tokens, debug):
    if openai_key == None:
        print('Please set your OpenAI key in config.py')
        return
    try:
        logs = interactive_chat(slow_status, engine, max_tokens, debug)
    except KeyboardInterrupt:
        print('You have interrupted your session. It has been terminated, with no logfiles saved.')
        return
    except EOFError:
        print('You have interrupted your session. It has been terminated, with no logfiles saved.')
        return
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
