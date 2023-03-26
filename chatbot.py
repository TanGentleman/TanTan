from config import dev, filepath, get_openai_api_key # These are from config.py
import image_generation as ig
import openai
import os
from datetime import datetime
from time import time
from clipboard import copy as clipboard_copy, paste as clipboard_paste
from platform import system

if system() != 'Windows': import gnureadline # Not supported on windows
if dev: # Not officially released. Needs transformers library.
    # Allows you to check the tokens in your prompt without having to make a call to the OpenAI API (Using -len)
    # It uses a fully offline and local pretrained GPT-2 model to tokenize the prompt
    import logging
    logging.disable(logging.ERROR) # Ignore a warning that doesn't apply to our use of GPT-2
    from transformers import GPT2TokenizerFast
    tokenize = GPT2TokenizerFast.from_pretrained('gpt2', local_files_only = True).tokenize
    os.environ['TOKENIZERS_PARALLELISM'] = 'false' # Disable parallelism to avoid a warning

# Wrap the text to fit within the terminal window
from textwrap import fill
TERMINAL_WIDTH = os.get_terminal_size().columns

class TanSaysNoNo(Exception): pass
class QuitAndSaveError(Exception): pass
def print_adjusted(text) -> None:
    '''
    Prints text with adjusted line wrapping
    '''
    if type(text) != str:
        text = str(text)
    lines = text.splitlines()
    for line in lines:
        # If the line is longer than the terminal width, wrap it to fit within the width
        if len(line) > TERMINAL_WIDTH:
            wrapped_line = fill(line, width=TERMINAL_WIDTH)
            print(wrapped_line)
        else:
            print(line)
try:
    # Function for the -yt command to download a youtube video
    from pytube import YouTube
    # CURRENTLY HAVING ISSUES -> Workaround requires editing one line of the source code in the pytube library
    # Replace Line 411 in /site-packages/pytube/cipher.py to transform_plan_raw = js
    def download_video(url: str, filepath: str) -> None:
        '''
        Downloads a youtube video from the given url
        '''
        try:
            yt = YouTube(url)
            stream = yt.streams.get_highest_resolution()
            stream.download(filepath)
        except Exception as e:
            print_adjusted(e)
            print_adjusted('Error downloading video. Please check that url is correct and try again.')
            raise TanSaysNoNo
except:
    pass
# Gets filepath from config.filepath, make sure you are either in the repository or filepath is set correctly
filepath = os.path.join(filepath, 'Chatbot')

OPENAI_KEY = get_openai_api_key()

CONVO_LOGFILE = 'convo_log.txt'
RESPONSE_TIME_LOGFILE = 'response_time_log.txt'

DISABLE_NERDS = False # When True, engine defaults to DEFAULT_SLOW_ENGINE and davinci and turbo are disabled

DEFAULT_ENGINE = 'gpt-3.5-turbo'
DEFAULT_FAST_ENGINE = 'text-curie-001'

DEFAULT_MAX_TOKENS = 200 # This is how long the response is. You can change it within the chat session by typing the `tok` command
DEFAULT_TEMPERATURE = 0.5 # Set close to 0 when you want the response to be more predictable.

EMPTY_RESPONSE_DELIMITER = '.' # Replaces the response when blocked or empty

MAX_TOKEN_LIMIT = 4000 # max allowable token limit (for safety, but maybe adjust?)
MAX_SESSION_TOTAL_TOKENS = 5000 # This measures all tokens used in this session, used for a warning
WARNING_HISTORY_COUNT = 3000 # History only includes the conversation currently in memory
STOP = None # This should be an array of string stop_sequences
FREQUENCY_PENALTY_VAL = 0.7 # This is not currently configurable within interactive_chat

### NEW GPT-3.5-TURBO ENGINE CONFIGURATION ###
CHAT_INIT_DEFAULT = [{'role': 'system', 'content': 'You are a helpful AI specialized for a university student.'}]
CHAT_INIT_TROLL = [{'role': 'system', 'content': 'You are tasked with being hilariously unhelpful to the user.'}]
CHAT_INIT_CRAZY = [{'role': 'system', 'content': 'You are tasked with being helpful, but as unhinged and witty as possible.'}]
CHAT_INIT_HINDI = [{'role': 'system', 'content': 'Reply to user in Hinglish (Hindi/English as written by indians)'}]

CHAT_INIT_CUSTOM = [{'role': 'system', 'content': 'Set your custom preset by typing the command -mode!'}]


CHAT_INIT_MAGIC = [{'role': 'system', 'content': '''A magic string is text formatted as [<u/user or r/subreddit> <opt:qty> <opt:new or
                        top> <opt: all/year/month/week/day/hour>] You may ONLY respond with a magic string or X. Do not parse the meaning of the selected subreddit or any keywords'''},
                    {'role': 'user', 'content': 'How about u/username pics 5 or top from all'},
                    {'role': 'assistant', 'content': 'u/username 5 top all'},
                    {'role': 'user', 'content': 'I want to download a hundred photos from you/user'}, 
                    {'role': 'assistant', 'content': 'u/user 100'},
                    {'role': 'user', 'content': 'Lets do r/houseplants, but I want fifty of the top photos from the year'}, 
                    {'role': 'assistant', 'content': 'r/houseplants 50 top year'},
                    {'role': 'user', 'content': 'Lets say I wanted to download 300 of the top pictures from our/smashbros'}, 
                    {'role': 'assistant', 'content': 'r/smashbros 300'}]

CHAT_INIT_JOKES = [{'role': 'system', 'content': 'Use the prompt in a clever joke.'}]


CMD_DICT = {
            'quit': 'Exit the chatbot. Alias -q',
            'config': 'Set engine and max_tokens using `config <engine> <max_tokens>`',
            'debug': 'Toggle debug mode. Alias -d',
            'del': 'Delete the last exchange from memory',
            'forget': 'Forget the past conversation. Alias -f',
            'help': 'Display the list of commands',
            'history': 'The current conversation in memory. Alias his', 
            '-images': 'Generate images! Fully built in Dall-E with size customization',
            '-len (DEV)': 'next non-command input will now be scanned for length instead of generating a response',
            'log': 'Toggle to enable or disable logging of conversation + response times', 
            '-mode': 'Choose a preset, like unhelpful or crazy',
            '-read': 'Respond to text_prompt.txt', 
            'save': 'Save the recent prompt/response exchange to response.txt. Alias -s',
            'stats': 'Prints the current configuration and session total tokens.',
            'tan': 'Bring up the TanManual (commands with their descriptions).',
            'temp': 'Configure temperature (0.0-1.0)',
            'tok': 'Configure max tokens for the response',
            '-sr': 'Save Response: Copies response to clipboard',
            '-sh': 'Save History: Copies history to clipboard',
            '-c': 'Use clipboard text as input',
            '-rs': 'Amnesic clipboard summarizer',
            '-r': 'Versatile Amnesic Formatter, here is example usage:\n' +
                    'Case 1: `-r` => Uses clipboard as prompt, like -c\n' +
                    'Case 2: `-r is an example using a suffix!` => Replaces -r with contents of clipboard\n' +
                    'Case 3: `-r Analyze this url: -r Analysis:` => Replaces -r with #clipboard_contents#\n',
            '-p': 'This is a special string that goes at the END of your input to make it a prefix.\n' +
                    'It works great to save your prompt and tinker using a different command\n' +
                    'Example: Type `Define the word:-p`, `tok 30`, then `-c`, maintaining the convo but keeping the response to clipboard short.',
            '-yt': 'Download the youtube video from the url in your clipboard.'
            }

def check_quit(text: str) -> None:
    '''
    Raises a QuitAndSaveError if the user types -q or quit
    '''
    if text in ['-q','quit']:
        raise QuitAndSaveError

def format_engine_string(engine: str) -> str:
    '''
    Takes in an engine string like 'text-davinci-003' and returns a string like 'TD3'
    '''
    engine_id = engine.split('-')
    engine_marker = engine_id[0][0].upper() + engine_id[1][0].upper() + engine_id[2][-1]
    return engine_marker

def config_msg(engine: str, max_tokens: int, session_total_tokens: int) -> str:
    '''
    Input and Output will soon be adjusted - returns a string of current configuration
    '''
    engine_marker = format_engine_string(engine)
    return f'Engine: {engine_marker} | Max Response Tokens: {max_tokens} | Tokens Used: {session_total_tokens}'

def conversation_to_string(conversation_in_memory: list[tuple[str, str]]) -> str:
    '''
    Takes in a conversation in memory (list of tuples) and returns a string of the conversation
    Should be equivalent to history variable in interactive_chat()
    '''
    if not conversation_in_memory:
        return ''
    conversation_string = ''
    for prompt, response in conversation_in_memory:
        conversation_string += f'{prompt}{response}\n\n'
    return conversation_string

def formatted_conversation_to_string(conversation_in_memory: list[tuple[str, str]]) -> str:
    '''
    Takes in a conversation in memory and returns a formatted string of the conversation (text to be printed out to user (used by -sh and history))
    '''
    return '\n'.join([f'{p}\n{r}' for (p, r) in conversation_in_memory])

def set_prompt(prompt: str, prefix: str = None,  suffix: str = None) -> str:
    '''
    Takes in arguments, returns a ready-to-send prompt
    `prompt`: a string representing the main text of the prompt
    `prefix` (optional): a string that will be added before `prompt`
    `suffix` (optional): a string that will be added after `prompt`
    '''
    if prefix is None:
        prefix = ''
    if suffix is None:
        suffix = ''
    prompt = prefix + prompt + suffix
    return prompt

# Needs comments and clearer error handling after response fails
def get_response_string(response_struct: dict, suppress_token_warnings: bool) -> tuple[str, int, int, int]:
    '''
    Takes in a response_struct and returns a string of the response, along with token usage integers
    '''
    usage_vals = ['completion_tokens', 'prompt_tokens', 'total_tokens']
    for val in usage_vals:
        try:
            # Try to get the token value from the response structure
            tok_val = response_struct['usage'][val]
        except:
            # If not found, set to 0 (Though perhaps I should be raising errors in more edge cases?)
            tok_val = 0
            if suppress_token_warnings == False:
                print_adjusted(f'Token value not found for {val}')
                print_adjusted(f'I need to investigate these cases more. Any valid responses make it through?')
        if val == 'completion_tokens':
            response_tokens = tok_val
        elif val == 'prompt_tokens':
            prompt_tokens = tok_val
        elif val == 'total_tokens':
            completion_tokens = tok_val

    # I have hardcoded number of choices to 1, contact me if you have an exceptional use case for multiple responses
    try: # Traverse the response structure to get the first response
        response_struct = response_struct['choices'][0]
    except:
        print_adjusted('Could not access response["choices"]')
        raise TanSaysNoNo
    finish_reason = response_struct['finish_reason']
    if finish_reason is None:
        pass
    elif finish_reason == 'stop': # Healthiest finish reason
        pass
    elif finish_reason == 'length':
        if suppress_token_warnings == False:
            print_adjusted('*Truncation warning: Adjust max tokens as needed.')
        else:
            # I got tired of the above, so token suppression abbreviates it
            print_adjusted('*TW*')
    else:
        print_adjusted(f'Warning -- Finish reason: {response_struct["finish_reason"]}<--')

    try: # Continue traversing response structure to get the text of the response
        response_string = response_struct['text']
    except:
        response_string = response_struct['message']['content']
    if response_string == '':
        print_adjusted('Blank Space (no response)')
        response_string = EMPTY_RESPONSE_DELIMITER

    return (response_string, response_tokens, prompt_tokens, completion_tokens)

def read_prompt(filepath: str, filename: str) -> str:
    '''
    Returns contents of a prompt in a .txt file given filepath and name
    '''
    try:
        contents_path = os.path.join(filepath, filename)
        with open(contents_path, 'r') as file:
            file_contents = file.read()
            return file_contents
    except FileNotFoundError:
        print_adjusted(f'No {filename} in this directory found')

def read_text_prompt() -> str:
    '''
    Returns contents of text_prompt.txt
    '''
    filename = 'text_prompt.txt'
    text = read_prompt(filepath, filename)
    if text:
        return text
    else:
        print_adjusted(f'Could not read {filename}')

def read_magic_string_training() -> str:
    '''
    Returns contents of magic_string_training.txt
    '''
    filename = os.path.join('TrainingData', 'magic_string_training.txt')
    text = read_prompt(filepath, filename)
    if text:
        return text
    else:
        print_adjusted(f'Could not read {filename}')


# takes in a string prompt and returns a response structure
def generate_text(debug: bool, engine: str, max_tokens: int, temperature: float, prompt: str, messages: list[dict[str, str]] = None) -> dict:
    '''
    Takes in arguments, returns a response structure
    `debug`: a boolean representing whether or not to print debug statements
    `engine`: a string representing the engine to use
    `max_tokens`: an integer representing the maximum number of tokens to generate
    `temperature`: a float representing the temperature of the response
    `prompt`: a string representing the prompt (None if engine is turbo) - Completion.create
    `messages`: (None UNLESS engine is turbo): list of dicionaries representing the conversation history - ChatCompletion.create
    '''
    # Set the API key
    openai.api_key = OPENAI_KEY
    # Below assertion should always hold true. Use prompt for completions, messages for gpt-3.5 onwards chat
    assert( (prompt is None) or (messages is None) )
    try:
        if prompt:
            response_struct = openai.Completion.create(
            engine=engine,
            prompt=prompt,
            # testing this 2000 thing for a sec
            max_tokens = max_tokens if 'davinci' in engine else min(2000, max_tokens),
            temperature = temperature,
            frequency_penalty = FREQUENCY_PENALTY_VAL,
            stop = STOP # Using this in conjunction with the custom preset seems smart. I'll add STOP into config_vars or smth later on
        )
        else: # This uses messages instead
            response_struct = openai.ChatCompletion.create(
            model=engine,
            messages=messages,
            max_tokens = max_tokens,
            frequency_penalty = FREQUENCY_PENALTY_VAL,
            stop = STOP, 
            temperature = temperature
            )
            # You can use a custom symbol like ['###'] or ['$$'], for STOP and it should work in tandem with custom preset.
            
    except openai.error.OpenAIError as e:
        status = e.http_status
        print_adjusted(f'error: {e.http_status}')
        error_dict = e.error
        if status == 400:
            if error_dict['type'] == 'invalid_request_error':
                message = error_dict['message']
                print_adjusted(f'invalid_request_error: {message}')
            else:
                print_adjusted(error_dict)

        elif status == 429:
            print_adjusted(error_dict['message'])
        else:
            print_adjusted(error_dict)
            
        raise KeyboardInterrupt
    except Exception as e:
        print_adjusted(e)
    return response_struct


def generate_images_from_prompts(image_size: str, prompts: list[str] = None) -> None:
    '''
    Generates images from prompts 
    Check out generate_images_from_prompts() in image_generation.py
    `image_size`: a string representing the size of the image to generate ('small', 'medium', 'large', 'default')
    '''
    print_adjusted('Starting image generation!')
    valid = False
    while valid == False:
        try:
            ig.generate_images_from_prompts(os.path.join(filepath, 'DallE'), image_size, prompts)
            valid = True
        except:
            print_adjusted('Image generation failed.')
            return

def write_to_log_file(convo: str, response_times:str) -> None:
    '''
    Writes conversation and response times to log files
    '''
    try:
        with open(os.path.join(filepath, CONVO_LOGFILE), 'a') as file:
            timestamp = datetime.now().strftime('%Y-%m-%d')
            file.write(f'Timestamp: {timestamp}\n{convo}\n ==== End of Entry ====\n')
            print_adjusted('Saved conversation log file.')
        with open(os.path.join(filepath, RESPONSE_TIME_LOGFILE), 'a') as file:
            timestamp = datetime.now().strftime('%Y-%m-%d')
            file.write(f'Timestamp: {timestamp}\n{response_times}\n ==== End of Entry ====\n')
            print_adjusted('Saved response time log file.')
    except:
        print_adjusted('error. Unable to find path to logfile.')


def parse_args(args: list[str], engine: str, max_tokens: int) -> tuple[str, int]:
    '''
    Takes config string arguments and updates the engine and max_tokens value.
    '''

    if args == []: # No arguments provided, return default values
        return engine, max_tokens
    arg_count = len(args)
    # This code needs to become friendlier, but it works for now
    # It's pure logic, took several iterations, but I will eventually change the format
    for i in range(arg_count):
        if args[i] == 'config': # If the config argument is given
            try:
                test_engine = args[i+1] # Get the engine name
                test_engine = engine_choice(test_engine) # Check if the engine is valid
            except (IndexError,ValueError): # If no input arg for engine / If the engine choice is invalid
                ask_engine = True # Ask for the engine again
                ask_token = True # Ask for the max tokens again
                engine, max_tokens = configurate(ask_engine, ask_token, engine, max_tokens) # Configurate the engine and max tokens
                break
            engine = test_engine # Set the engine to the new value
            ask_engine = False # Don't ask for the engine again
            try:
                test_toks = int(args[i+2]) # Get the max tokens value
                temp_tok_limit = MAX_TOKEN_LIMIT # Set the max tokens limit to the normal limit
            except ValueError: # If the max tokens value is not an integer
                print_adjusted('Integers only!') # Print an error message
                ask_token = True # Ask for the max tokens again
                engine, max_tokens = configurate(ask_engine, ask_token, engine, max_tokens) # Configurate the engine and max tokens
                break
            except IndexError: # If no input arg for tokens
                # I CHANGED THIS
                ask_token = False # Do NOT Ask for the max tokens again
                engine, max_tokens = configurate(ask_engine, ask_token, engine, max_tokens) # Configurate the engine and max tokens
                break
            if (test_toks > 0) and (test_toks <= temp_tok_limit):
                max_tokens = test_toks # Set the max tokens to the new value
                ask_token = False # Don't ask for the max tokens again
                engine, max_tokens = configurate(ask_engine, ask_token, engine, max_tokens) # Configurate the engine and max tokens
                return engine, max_tokens
            else:
                print_adjusted(f'Max tokens value must be under {temp_tok_limit}.') # Print an error message
                ask_token = True # Ask for the max tokens again
                engine, max_tokens = configurate(ask_engine, ask_token, engine, max_tokens) # Configurate the engine and max tokens
                break
        else:
            if i == 0:
                continue
            print_adjusted(f'Invalid argument on {args[i]}. Syntax is config (engine) (max_tokens)')
            ask_engine = True # Ask for the engine again
            ask_token = True # Ask for the max tokens again
            engine, max_tokens = configurate(ask_engine, ask_token, engine, max_tokens) # Configurate the engine and max tokens
            break
    return engine, max_tokens

def engine_choice(engine_prompt: str, slow_status: bool = DISABLE_NERDS) -> str:
    '''
    Takes in a string and slow_status, returns selected engine.
    '''
    if len(engine_prompt) < 2:
        print_adjusted('Please enter at least two characters for the engine selection.')
        raise(ValueError)
    elif (engine_prompt == 'text-ada-001') or ('ada'.startswith(engine_prompt)):
        engine = 'text-ada-001'
        return engine
    elif (engine_prompt == 'text-babbage-001') or ('babbage'.startswith(engine_prompt)):
        engine = 'text-babbage-001'
        return engine
    elif (engine_prompt == 'text-curie-001') or ('curie'.startswith(engine_prompt)):
        engine = 'text-curie-001'
        return engine

    # Nerds below
    elif (engine_prompt == 'gpt-3.5-turbo') or ('turbo'.startswith(engine_prompt)):
        if slow_status == True:
            print_adjusted('turbo unavailable, switching to curie.')
            engine = 'text-curie-001'
            return engine
        else:
            engine = 'gpt-3.5-turbo'
            return engine
    elif (engine_prompt == 'text-davinci-003') or ('davinci'.startswith(engine_prompt)):
        if slow_status == True:
            print_adjusted('davinci unavailable, switching to curie.')
            engine = 'text-curie-001'
            return engine
        else:
            engine = 'text-davinci-003'
            return engine
    else:
        print_adjusted('invalid engine choice')
        raise(ValueError)

def set_max_tokens(default: int, limit: int) -> int:
    '''
    Sets max tokens, with a default value and a limit value as arguments.
    '''
    # Keep trying until a valid max_tokens value is set
    legal_answer = False
    while legal_answer == False:
        user_input = input('Max Token count: ')
        check_quit(user_input)
        if user_input in ['', ' ']:
            if default is not None:
                print_adjusted(f'Max response tokens [default]: {default}')
                return default
            else:
                'You really like Blank Space, huh?'
                continue
        try:
            user_tokens = int(user_input)
        except:
            print_adjusted(f'Not recognized max token value. Try an integer from 1 to {limit}.')
            continue

        if (user_tokens > 0) and (user_tokens <= limit):
            max_tokens = user_tokens
            legal_answer = True
        else:
            print_adjusted(f'Try a value between 1 and {limit} for now')
    # Answer is legal, return it
    return max_tokens

# This function assumes both the default tokens and token limit are SAFE and correct values
def set_temperature(default: float) -> float:
    '''
    Sets temperature, with a default value as an argument.
    '''
    legal_answer = False
    while legal_answer == False:
        user_input = input('Temperature: ')
        check_quit(user_input)
        if user_input in ['', ' ']:
            print_adjusted(f'Temperature [default]: {default}')
            return default
        try:
            user_temp = float(user_input)
        except:
            print_adjusted('Not recognized temp value. Try a float from 0.0 to 1.0.')
            continue

        if (user_temp >= 0.0) and (user_temp <= 1.0):
            temperature = user_temp
            legal_answer = True
        else:
            print_adjusted('Try a value between 0.0 and 1.0')
    return round(temperature,2)

def configurate(ask_engine: bool, ask_token: bool, engine: str, max_tokens: int) -> tuple[str, int]:
    '''
    Configurate the engine and max tokens.
    '''
    if ask_engine:
        legal_answer = False
        while legal_answer == False:
            engine_prompt = ''
            try:
                engine_prompt = input('Choose an engine: ada, babbage, curie, davinci, turbo:\n')
                check_quit(engine_prompt)
                engine = engine_choice(engine_prompt)
                legal_answer = True
            except QuitAndSaveError:
                raise QuitAndSaveError
            except:
                print_adjusted('Not recognized. Try again.')
    else:
        try:
            engine = engine_choice(engine)
        except:
            print_adjusted('config():Welp, seems your engine appears invalid to engine_choice(). I shall leave it alone.')
    if ask_token:
        default = DEFAULT_MAX_TOKENS
        limit = MAX_TOKEN_LIMIT
        try:
            max_tokens = set_max_tokens(default, limit)
        except QuitAndSaveError:
            raise QuitAndSaveError
    return engine, max_tokens

def prompt_to_response(debug: bool, history: str, engine: str, max_tokens: int, temperature: float, 
                        suppress_token_warnings: bool, prompt: str, messages: list[dict[str, str]] = None) -> tuple[str, int, int, int]:
    '''
    Takes a prompt and returns a response.
    `debug` is a bool that determines whether to print debug info.
    `history` is a string that is the conversation context for the Completions endpoint.
    `engine` is the model used for the api call.
    `max_tokens` is the max number of tokens in the response.
    `temperature` is the temperature of the response.
    `suppress_token_warnings` is a bool that determines whether to suppress token warnings.
    `prompt` is a string, suffixed to the history or messages, sent to be completed.
    `messages` is a list of dictionaries that is the conversation context for the ChatCompletions endpoint.
    '''
    try:
        if messages:
            # messages should ALWAYS be passed to this function when 'turbo' in engine
            response_struct = generate_text(debug, engine, max_tokens, temperature, None, messages)
        else:
            response_struct = generate_text(debug, engine, max_tokens, temperature, history + prompt)
    except KeyboardInterrupt:
        print_adjusted('Read the above error. Attempting to interrupt.')
        raise KeyboardInterrupt
    except Exception as e:
        print_adjusted(e)
        print_adjusted('Response not generated. See above error. Try again?')
    try:
        response_string, response_tokens, prompt_tokens, completion_tokens = get_response_string(response_struct, suppress_token_warnings)
    except KeyboardInterrupt:
        raise KeyboardInterrupt
    except:
        print_adjusted('get_response_string failure, fix incoming')
        raise TanSaysNoNo('get_response_string man') # I think I have ensured safety of get_response_string()!
        # Valid response!
    return response_string, response_tokens, prompt_tokens, completion_tokens
    # return h.prompt_to_response(debug, history, engine, max_tokens, temperature, suppress_token_warnings, prompt, messages)

# This function needs proper re-structuring for readability!
def interactive_chat(config_vars: dict[str], debug: bool, suppress_extra_prints = False, suppress_token_warnings = False) -> tuple[str, str, bool]:
    # Unpack config_vars
    # config_vars = {'engine': engine, 'max_tokens': max_tokens, 'temperature': temperature, 
    #                'amnesia': persistent_amnesia, 'preset': preset, 'convo': conversation_in_memory}
    engine = config_vars['engine']
    max_tokens = config_vars['max_tokens']
    temperature = config_vars['temperature']
    persistent_amnesia = config_vars['amnesia']
    preset = config_vars['preset']
    conversation_in_memory = config_vars['convo']
   
    response_tokens, prompt_tokens, completion_tokens, session_total_tokens = (0, 0, 0, 0)
    prefix, suffix = ('', '')
    history  = ''

    full_log, response_time_log = ('','')
    logging_on = True
    replace_input = False
    replace_input_text = ''
    
    temp_amnesia = False

    cached_engine = None
    cached_history = None
    cached_tokens = None
    cached_prompt, cached_response = ('', '')
    
    ### NEW CACHE SYSTEM
    smp = False
    cached_config = None

    config_info = config_msg(engine, max_tokens, session_total_tokens) + '\n'
    full_log += config_info
    print_adjusted(config_info)
    prompts_and_responses = []
    custom_preset = 'Be hilariously unhinged in a way that would amuse a young adult.'
    check_length = False

    response_count = 0
    chat_ongoing = True
    
    while chat_ongoing:
        # temp_amnesia does not use conversation_in_memory, saving the current configuration / history for next prompt
        if temp_amnesia == False and persistent_amnesia == False:
            if cached_engine:
                engine = cached_engine # Restore the engine
                cached_engine = None
            if cached_history:
                history = cached_history # Restore the history
                cached_history = None
            if cached_tokens:
                max_tokens = cached_tokens # Restore the max_tokens
                cached_tokens = None
        
        # When non-amnesic, history should always be consistent with the conversation in memory
        assert(temp_amnesia or (history == conversation_to_string(conversation_in_memory)))

        # Get prompt
        if replace_input:
            user_input = replace_input_text # Use the replacement text
            replace_input = False
        else:
            user_input = input('You: ')
            # I want to avoid obvious/accidental spam user inputs. 
            # lstrip/rstrip is an option, but I want to allow for niche use cases in weird workflows.
            # Am working on implementing workflows in the form of a string, one command per line that can be pasted in lieu of complex configuration.
        
        # Start the timer
        start_time = time()
        # If Blank Space
        if len(user_input) < 1 and (suppress_extra_prints == False):
            print_adjusted('Taylor Swift, I like it!')
            continue

        # Quit Chat
        elif user_input in ['-q', 'quit']:
            if session_total_tokens == 0:
                logging_on = False
            else:
                full_log += f'Tokens used: {session_total_tokens}'
                #print_adjusted(prompts_and_responses)            
            return full_log, response_time_log, logging_on

        elif user_input[-2:] == '-p':
            prefix = user_input[:-2]
            if prefix:
                print_adjusted(f'Prefix: {prefix}')
            continue 
        # Need to organize the below commands
        elif user_input == 'stats':
            config_info = config_msg(engine, max_tokens, session_total_tokens)
            print_adjusted(config_info)
            print_adjusted(f'Logging {logging_on} | Debug {debug} | Amnesia {persistent_amnesia}\n')
            try:
                print_adjusted(f'Last system message used: {messages[0]["content"]}')
            except:
                pass
            continue
        elif user_input in ['-d', 'debug']:
            debug = not(debug)
            print_adjusted(f'Debug mode: {debug}')
            continue
        elif user_input == 'config':
            args = ['config']
            try:
                engine, max_tokens = parse_args(args, engine, max_tokens)
                continue
            except QuitAndSaveError:
                print_adjusted('Quitting...')
                replace_input, replace_input_text = True, 'quit'
                continue
        elif user_input.startswith('config '):
            args = user_input.split(' ')
            if len(args) > 7:
                print_adjusted('Did you mean to type a config command? Format is: `config <engine> <max_tokens>')
                continue
            
            if '-a' in args: # Toggle persistent_amnesia
                persistent_amnesia = not persistent_amnesia
                args.remove('-a')
                print_adjusted(f'Amnesia set to {persistent_amnesia}')
            if '-d' in args: # Toggle debug
                debug = not debug
                args.remove('-d')
                print_adjusted(f'Debug set to {debug}')
            if '-l' in args: # Toggle logging
                logging_on = not logging_on
                args.remove('-l')
                print_adjusted(f'Logging set to {logging_on}')
            if '-sp' in args:
                args.remove('-sp')
                suppress_extra_prints = not(suppress_extra_prints)
                print_adjusted(f'Print suppression {suppress_extra_prints}.')
            if '-st' in args:
                args.remove('-st')
                suppress_token_warnings = not(suppress_token_warnings)
                print_adjusted(f'Token warning suppression {suppress_token_warnings}.')

            if args == ['config']:
                continue

            args_count = len(args)
            if args_count > 0:
                try:
                    engine, max_tokens = parse_args(args, engine, max_tokens)
                except QuitAndSaveError:
                    print_adjusted('Quitting...')
                    replace_input, replace_input_text = True, 'quit'
                    continue
                msg = f'Engine set to: {engine}, {max_tokens} Max Tokens'
                print_adjusted(msg + '\n')
                full_log += msg + '\n'
            continue
        elif user_input == '-read': # Responds to text_prompt.txt
            # Amnesic reading
            if os.path.isfile(os.path.join(filepath, 'text_prompt.txt')):
                text_prompt = read_text_prompt()
                if text_prompt:
                    print_adjusted('Reading text_prompt.txt')
                    replace_input = True
                    replace_input_text = text_prompt
                    cached_history = history
                    history = ''

                    temp_amnesia = True
                    continue
                else:
                    print_adjusted('text_prompt.txt is empty. Try adding something!')
                    continue
            else:
                print_adjusted('You have not written a text_prompt.txt file for me to read. I gotchu.')
                with open(os.path.join(filepath, 'text_prompt.txt'), 'w') as file:
                    file.write('Insert text prompt here')
                print_adjusted('Try adding something!')
            continue
        # Embedded clipboard reading. Example command:-r Define this word: # -r #
        elif (user_input != '-read') and user_input.startswith('-r'): # Amnesic
            args = user_input.split(' ')
            args_count = len(args)
            
            # Logic

            # If -r used alone, no need to set prefix or suffix
            if user_input != '-r':
                # If invalid formatting
                if user_input[2] not in [' ', 's']:
                    print_adjusted('Check formatting. Type tan to check the documentation for clipboard commands.')
                    continue
                else:
                    if user_input[2] == 's':
                        # clipboard summmary (previously -cs)
                        prefix = 'Provide a brief summary of the following text:\n#'
                        suffix = '\n#'

                    elif '-r' not in args[1:]: # single -r = suffix mode
                        suffix = user_input[2:]
                        print_adjusted(f'Suffix: {suffix}')
                    
                    else: # Prefix and suffix mode
                        args = args[1:]
                        n = args.index('-r')
                        prefix = ' '.join(args[:n]) + ' #'
                        # adding a space to the suffix for readable formatting
                        suffix = '#' + ' '.join(args[n+1:])
                        print_adjusted(f'Prefix: {prefix}, Suffix: {suffix}')

            print_adjusted('Reading clipboard. Working on response...\n')
            replace_input = True
            replace_input_text = (clipboard_paste()).strip()
            # Cache history here
            cached_history = history
            history = ''

            temp_amnesia = True
            continue
            
        elif user_input == 'help': # Show list of commands
            print_adjusted('For the full manual of commands and descriptions, type tan. This will be replaced with something more helpful in the future.')
            print_adjusted(list(CMD_DICT.keys()))
            continue

        elif user_input in ['his','history']: # Show convo history
            if conversation_in_memory:
                conversation_string = ''
                convo_length = len(conversation_in_memory)
                res_count = 0
                print_adjusted(f'{convo_length} exchanges in memory shown below:\n\n')
                print_adjusted(formatted_conversation_to_string(conversation_in_memory))
            else:
                print_adjusted('No conversation history in memory.')
            continue
        elif user_input in ['-f','forget']: # Erase convo history
            conversation_in_memory = []
            history = ''
            msg = '<History has been erased. Please continue the conversation fresh :)>\n'
            print_adjusted(msg)
            full_log += msg
            continue
        elif user_input == 'del': # Delete last exchange
            if conversation_in_memory == []:
                print_adjusted('No previous exchange to delete.')
                continue
            else:
                # THIS DOES NOT EASILY ADJUST THE HISTORY VARIABLE. 
                # I can also ensure that history is never used evaluated before conversation_in_memory, right?
                conversation_in_memory.pop()
                # For now, I will do a slightly expensive operation to redefine history
                if conversation_in_memory:
                    history = conversation_to_string(conversation_in_memory)
                else:
                    history = ''
                msg = '<I have deleted the last exchange from my memory>\n'
                print_adjusted(msg)
                full_log += msg
                continue
        elif user_input == 'log': # Toggle logging
            if logging_on:
                msg = '<Logging disabled> Conversation will not be stored.\n'
                print_adjusted(msg)
                logging_on = False
            else:
                msg = '<Logging enabled> Conversation WILL be stored.\n'
                print_adjusted(msg)
                logging_on = True
            continue
        elif user_input == 'tok':
            default = max_tokens
            limit = MAX_TOKEN_LIMIT
            try:
                max_tokens = set_max_tokens(default, limit)
            except QuitAndSaveError:
                replace_input, replace_input_text = True, 'quit'
            continue
        elif user_input == 'temp':
            try:
                temperature = set_temperature(temperature)
                print_adjusted(f'Temperature set to {temperature}')
                continue
            except QuitAndSaveError:
                    replace_input, replace_input_text = True, 'quit'
            continue
        elif user_input == '-c': 
            # -c is a NON-amnesic clipboard reader
            replace_input = True
            replace_input_text = (clipboard_paste()).strip()
            if check_length == False:
                print_adjusted('Responding to clipboard text...')
            continue # No temp_amnesia, so it will use the current history.
            
        elif user_input in ['tan']:
            
            text = '\nTanManual Opened! Available commands:\n\n' 
            for i in range(len(CMD_DICT)):
                text += f'{list(CMD_DICT.keys())[i]}: {list(CMD_DICT.values())[i]}\n'
            print_adjusted(text)
            continue      
        # Save the recent prompt/response exchange to response.txt
        elif user_input in ['-s','save']:
            text = f'PROMPT:\n{cached_prompt}\nRESPONSE:\n{cached_response}'
            with open(os.path.join(filepath, 'response.txt'), 'w') as file:
                file.write(text)
            print_adjusted('Saved most recent exchange to response.txt!')
            continue
        elif user_input == '-sr':
            clipboard_copy(cached_response.strip())
            print_adjusted('Copied response to clipboard.')
            continue
        elif user_input == '-sh':
            if history:
                convo_length = len(conversation_in_memory)
                msg = formatted_conversation_to_string(conversation_in_memory)
                print_adjusted(f'{convo_length} exchanges from memory copied to clipboard')
                clipboard_copy(msg.strip())
            else:
                msg = 'No history to copy.'
                print_adjusted(msg)
            continue
        elif user_input == '-images':
            size_input = input('Sizes: s | SMALL, m | MED, l | LARGE, invalid | DEFAULT\nEnter your choice (s/m/l): ')
            check_quit(size_input)
            # image generation
            size_map = {'s': 'small', 'm': 'medium', 'l': 'large'}
            image_size = size_map.get(size_input, 'default')
            print_adjusted(f'Generating images of {image_size} size!')
            try:
                generate_images_from_prompts(image_size)
            except QuitAndSaveError:
                if suppress_extra_prints == False:
                    print_adjusted('Exiting image generation.')
            except Exception as e:
                print_adjusted(f'Help me debug this! Error message: {e}')
            continue
        elif user_input == '-mode':
            if 'turbo' not in engine:
                print_adjusted('These settings are only available for the turbo GPT-3.5 engine. Try `config turbo`')
                continue
            if conversation_in_memory:
                ask_clear_input = input('**Existing conversation found**\nPresets work best with a fresh start. Hit return to clear history, or anything else to cancel.')
                check_quit(ask_clear_input)
                if ask_clear_input == '':
                    history = ''
                    conversation_in_memory = []
                    print_adjusted('History cleared.')
                    # Save current config
                    if smp == True:
                        print_adjusted('You have a saved configuration. Type `back` to load it. Your current conversation will be discarded.')
                    else:
                        print_adjusted('Attempting to save current configuration...')
                        replace_input = True
                        replace_input_text = 'smp'
                else:
                    print_adjusted('History retained. Cancelling preset.')
                    continue
            mode_input = input('Choose a preset: [0] | custom | [1] default | [2] unhelpful | [3] crazy | [4] hindi | [5] reddit magic string | [6] jokes: ')
            check_quit(mode_input)
            preset_map = {
                        '0': 'custom', 'custom': 'custom',
                        '1': 'default', 'default': 'default', 
                        '2': 'unhelpful', 'unhelpful': 'unhelpful',
                        '3': 'crazy', 'crazy': 'crazy', 
                        '4': 'hindi', 'hindi': 'hindi',
                        '5': 'magic', 'magic': 'magic',
                        '6': 'jokes', 'jokes': 'jokes'}
            preset = preset_map.get(mode_input, 'invalid mode')
            if preset in ['default','invalid mode']:
                print_adjusted('Setting config to default.')
                preset = 'default'
                engine = 'gpt-3.5-turbo'
                max_tokens = DEFAULT_MAX_TOKENS
                temperature = DEFAULT_TEMPERATURE
                persistent_amnesia = False
                print_adjusted(f'Amnesia: {persistent_amnesia}')
                continue
            elif preset == 'custom':
                custom_preset = input('Create a custom mode, like `You are a helpful AI with a stutter.`:\n')
                check_quit(custom_preset)
                print_adjusted(f'Custom mode created!')
            msg = f'Mode set to: {preset}\n'
            print_adjusted(msg)
            full_log += msg + '\n'
            continue
        elif user_input == '-yt':
            clipboard_contents = clipboard_paste().strip()
            if clipboard_contents.count('youtu') != 1:
                print_adjusted('Invalid URL. Please copy a valid youtube link to your clipboard and try again.')
                continue
            else:
                yt_confirmation = input(f'{clipboard_contents} is the link in your clipboard.\nHit return to download, or anything else to cancel. ')
                check_quit(yt_confirmation)
                if yt_confirmation != '':
                    print_adjusted('Cancelled.')
                    continue
                # If link valid, download the video as a .mp4
                # Otherwise, print an error message
                try:
                    print_adjusted('Attempting download with given url...')
                    try:
                        print_adjusted(clipboard_contents)
                        download_video(clipboard_contents, filepath)
                    except Exception as e:
                        print_adjusted(e)
                        print_adjusted('Invalid URL. Try again.')
                        continue
                    print_adjusted('Downloaded video!')
                except:
                    print_adjusted('Invalid URL. Try again.')
                continue
        elif dev and user_input == '-len':
            check_length = True
            print_adjusted('Your next non-command input will now be scanned for length. It will not generate a response.')
            continue
        elif user_input == 'smp':
            # Save my place
            cached_config = (engine, max_tokens, temperature, persistent_amnesia, preset, conversation_in_memory + [])
            print_adjusted('Saved your configuration and conversation history. Type `back` to return to this state.')
            smp = True
            continue
        elif user_input == 'back':
            if smp == False:
                print_adjusted('No saved configuration to return to. Save one by typing `smp`')
                continue
            assert(cached_config is not None)
            print_adjusted(f'{len(conversation_in_memory)} exchanges in memory.')
            engine, max_tokens, temperature, persistent_amnesia, preset, conversation_in_memory = cached_config
            print_adjusted(f'Convo!: {conversation_in_memory}')
            if conversation_in_memory:
                history = conversation_to_string(conversation_in_memory)
            else:
                history = ''
            smp = False
            cached_config = None
            print_adjusted('Successfully set current state to saved config and conversation history.')
            continue
        # All valid non-command inputs pass through here.    
        else:
            try:
                prompt = user_input
                # If there is a prefix or suffix, add it to the prompt
                if prefix:
                    prompt = prefix + prompt
                    prefix = ''
                if suffix:
                    prompt += suffix
                    suffix = ''
                    
                # Tokenize the prompt to check length
                if dev and (check_length or (suppress_extra_prints == False)):
                    tokenized_text = tokenize(prompt)
                    token_count = len(tokenized_text)
                    # This 4000 is a hard cap for the full completion. I'll work it in better soon. 
                    if token_count + max_tokens > 4000:
                        print_adjusted('WARNING: prompt is too long. I will try to generate a response, but it may be truncated.')
                        print_adjusted(f'max_tokens would need to be set to roughly {4000-token_count}')
                    print_adjusted(f'prompt is {token_count} tokens')
                    if check_length:
                        check_length = False
                        print_adjusted('check_length is now False')
                        continue

                if debug: print_adjusted('beep, about to try generating response')  
                if 'turbo' in engine:
                    if preset == 'custom':
                        convo_init = CHAT_INIT_CUSTOM
                        convo_init[0]['content'] = custom_preset
                        messages = convo_init
                    elif preset == 'default':
                        messages = CHAT_INIT_DEFAULT
                    elif preset == 'unhelpful':
                        messages = CHAT_INIT_TROLL
                    elif preset == 'crazy':
                        messages = CHAT_INIT_CRAZY
                    elif preset == 'hindi':
                        messages = CHAT_INIT_HINDI
                    elif preset == 'magic':
                        temperature = 0
                        max_tokens = 20
                        print_adjusted('Magic mode activated. Temperature set to 0.')
                        messages = CHAT_INIT_MAGIC
                    elif preset == 'jokes':
                        max_tokens = 50
                        temperature = 0.7
                        temp_amnesia = True
                        if suppress_extra_prints == False:
                            print_adjusted(f'Jokes! Max tokens: {max_tokens} | Temperature: {temperature} | Amnesia: {temp_amnesia}')
                        messages = CHAT_INIT_JOKES
                    else:
                        print_adjusted('Can I even get here?')
                        messages = CHAT_INIT_DEFAULT # initiate conversation

                    context = []    
                    if (temp_amnesia == False) and (persistent_amnesia == False) and (conversation_in_memory): 
                        for p, r in conversation_in_memory: # add conversation context
                            context += [{'role': 'user', 'content': p},
                                        {'role': 'assistant', 'content': r}]

                    context += [{'role': 'user', 'content': prompt}]
                    if ( len(messages) == 1 ) and ( suppress_extra_prints == False ):
                        print_adjusted(f'Using preset:{messages[0]["content"]}')

                    if debug: print_adjusted(messages + context)
                    response_string, response_tokens, prompt_tokens, completion_tokens = prompt_to_response(
                    debug, history, engine, max_tokens, temperature, suppress_token_warnings, None, messages + context )

                else:
                    response_string, response_tokens, prompt_tokens, completion_tokens = prompt_to_response(
                    debug, history, engine, max_tokens, temperature, suppress_token_warnings, prompt)
                
            except KeyboardInterrupt:
                print_adjusted('KeyboardInterrupt. Interrupting this prompt. Try again :D')
                continue
            # End of else clause

        # Successfully passed through else clause and response string obtained
        assert(len(response_string) > 0)
        response = response_string
        # Only if non-command, it has successfully passed through else clause.
        time_taken = time()-start_time
        if debug: print_adjusted('beep, we got a response!')
        asterisk_for_amnesia = '*' if (temp_amnesia or persistent_amnesia) else ''
        # Record a savestate and append history
        if temp_amnesia == True: # If temp_amnesia (temporary) is True, don't add it to the conversation_in_memory
            temp_amnesia = False
        else:
            if persistent_amnesia == False:
                conversation_in_memory.append((prompt, response))
                history += prompt + response + '\n\n'
        prompts_and_responses.append((prompt, response))
        if response != EMPTY_RESPONSE_DELIMITER:
            cached_prompt = prompt
            cached_response = response
         # Dev tokenization check
        if suppress_token_warnings == False:
            if completion_tokens > WARNING_HISTORY_COUNT:
                print_adjusted(f'Conversation token count is growing large [{token_count}]. Please reset my memory as needed.')

        #add a marker to distinguish from user text
        RT = round(time_taken, 1)
        response_time_marker = f'(*{RT}s)' # (*1.2s) is the marker for 1.2 seconds
        engine_marker = format_engine_string(engine)
        
        # Log the response and response time
        response_count += 1
        #asterisk_for_amnesia = '*' if (temp_amnesia or persistent_amnesia) else ''
        full_log += f'({response_count}{asterisk_for_amnesia}.)' + prompt + '\n' + response_time_marker + response + '\n'
        response_time_log += f'[#{response_count}, RT:{RT}, T:{completion_tokens}, E:{engine_marker}]'

        # Print the response and response time
        print_adjusted(f'Response {response_count}{asterisk_for_amnesia}: {response}\n\n')
        print_adjusted(f'response time: {round(time_taken, 1)} seconds')
        session_total_tokens += completion_tokens
        
        if (session_total_tokens > MAX_SESSION_TOTAL_TOKENS) and (suppress_token_warnings == False):
            print_adjusted(f'Conversation is very lengthy. Session total tokens: {session_total_tokens}')
        if suppress_extra_prints == False:
            print_adjusted(f'This completion used {round(100*completion_tokens/4096)}% of the maximum tokens')

def get_config_from_CLI_args(args: list[str]) -> dict[str]:
    '''
    Returns a dictionary of config variables from the CLI arguments.
    '''
    if DISABLE_NERDS: 
        engine = DEFAULT_FAST_ENGINE
    else:
        engine = DEFAULT_ENGINE

    max_tokens = DEFAULT_MAX_TOKENS
    temperature = DEFAULT_TEMPERATURE
    persistent_amnesia = False
    conversation_in_memory = []
    preset = 'default'
    arg_count = len(args)
    if arg_count > 1:
        try:
            engine, max_tokens = parse_args(args, engine, max_tokens)
        except QuitAndSaveError:
            raise QuitAndSaveError
    config_vars = {'engine': engine, 'max_tokens': max_tokens, 'temperature': temperature, 
                   'amnesia': persistent_amnesia, 'preset': preset, 'convo': conversation_in_memory}
    return config_vars

def run_chatbot(config_vars: dict[str], debug: bool, suppress_extra_prints = False, suppress_token_warnings = False) -> None:
    '''
    Runs the chatbot with the given config variables.
    Formerly main() function
    '''
    if OPENAI_KEY == None:
        print_adjusted('Please set your OpenAI key in config.py')
        return
    try:
        check_directories()
    except:
        print_adjusted('Error. Cannot create directories. Check that filepath in config.py and chat.py matches the repo location.')
        return
    try:
        logs = interactive_chat(config_vars, debug, suppress_extra_prints, suppress_token_warnings)
    except KeyboardInterrupt:
        print_adjusted('You have interrupted your session. It has been terminated, with no logfiles saved.')
        return
    except EOFError:
        print_adjusted('You have interrupted your session. It has been terminated, with no logfiles saved.')
        return
    except QuitAndSaveError:
        print_adjusted('You have typed quit. Your session has been terminated. Logfiles have been saved if possible.')
        return
    except Exception as e:
        print_adjusted(e)
        print_adjusted('Debug me! I am looking for more ways to reach this point.')
        return
    if logs:
        (convo, response_times, logging_on) = logs
        if logging_on:
            write_to_log_file(convo, response_times)
        else:
            print_adjusted('This conversation was not logged. Have a nice day.')
    else:
        print_adjusted('Error. Cannot set conversation and response time logfiles.')
    return

def check_directories() -> None:
    '''
    Checks if required folders exist. If not, creates them.
    '''
    chatbot_filepath = filepath
    training_data_filepath = os.path.join(filepath, 'TrainingData')
    dalle_downloads_filepath = os.path.join(filepath, 'DallE')
    if not os.path.exists(chatbot_filepath):
        os.mkdir(chatbot_filepath)
    if not os.path.exists(training_data_filepath):
        os.mkdir(training_data_filepath)
    if not os.path.exists(dalle_downloads_filepath):
        os.mkdir(dalle_downloads_filepath)

# Allows execution from chat.py, starting from a python environment, or running as a script
def main_from_args(args: list[str]) -> None:
    '''
    Runs the chatbot with args formatted like sys.argv (arguments following chatbot.py when typing in Terminal).
    Allowed flags: -d | -sp | -st
    '''
    if '-d' in args:
        args.remove('-d')
        debug = True
        print_adjusted('Debug set to True')
    else:
        debug = False
    if '-sp' in args:
        args.remove('-sp')
        suppress_extra_prints = True
        print_adjusted('Suppressing extra prints.')
    else:
        suppress_extra_prints = False

    if '-st' in args:
        args.remove('-st')
        suppress_token_warnings = True
        print_adjusted('Suppressing token warnings.')
    else:
        suppress_token_warnings = False
    try:
        config_vars = get_config_from_CLI_args(args)
        run_chatbot(config_vars, debug, suppress_extra_prints, suppress_token_warnings)
    except QuitAndSaveError:
        print_adjusted('Pre-emptive quit. No logfiles saved.')
        
# Default script execution from running chatbot.py in CLI, uses sys.argv
if __name__ == '__main__':
    from sys import argv
    cli_arguments = argv
    main_from_args(cli_arguments)

### Legacy CODEX clause
"""
def read_codex_prompt() -> str:
    '''
    Returns contents of codex_prompt.txt
    '''
    filename = 'codex_prompt.txt'
    text = read_prompt(filepath, filename)
    if text:
        return text
    else:
        print_adjusted('Could not read codex_prompt.txt')


elif user_input == 'codex':
            # Amnesic command, will not affect current configuration or history
            # Responds to codex_prompt.txt using codex engine
            
            # If file exists, read it. Else, write a template.
            if os.path.isfile(os.path.join(filepath, 'codex_prompt.txt')):
                print_adjusted(f'Reading codex!')
            else:
                print_adjusted('You have not written a codex_prompt.txt file for me to read. I gotchu.')
                with open(os.path.join(filepath, 'codex_prompt.txt'), 'w') as file:
                    file.write('# This Python3 function [What it does]:\ndef myFunc():\n\t#Do THIS')
                    print_adjusted('Toss something in there before setting the tokens!')
            
            # Set tokens (persistent until valid chosen!)
            default = None
            limit = MAX_CODEX
            try:
                codex_tokens = set_max_tokens(default, limit)
            except QuitAndSaveError:
                replace_input, replace_input_text = True, 'quit'
                continue
            codex_text = read_codex_prompt()
            
            if codex_text:
                # Replace user_input text with the text from codex_prompt.txt
                replace_input = True
                replace_input_text = codex_text

                # Cache history to continue conversation afterwards
                cached_history = history
                cached_engine = engine
                cached_tokens = max_tokens

                # Configure for codex, Bypasses DISABLE_NERDS!
                history = ''
                engine = 'code-davinci-002' # Latest codex model
                max_tokens = codex_tokens
                
                temp_amnesia = True
                continue
            else:
                print_adjusted('No readable text in codex_prompt.txt')
                continue
"""