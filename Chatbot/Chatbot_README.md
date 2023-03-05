# New way to run the chatbot from within a python environment:
1. Move chat.py to your home directory and configure default.
2. Run terminal command:
- `python -i -m chat`

# Type `tan` to see the current list of commands

# MacOS Shortcuts flow:
1. [Text]:python -i -m chat
2. Copy [Text] to clipboard
3. Open Terminal

# To run:
- Run shortcut
- Paste and hit return, violá
- To relaunch from python environment after quitting, simply type `import chat`

Command dictionary:
cmd_dict = {
            'config': 'Set the engine and max_tokens. `config [engine] [tokens] [-d]`',
            'codex': 'Generate a code completion from codex_prompt.txt',
            'debug': 'Toggle debug mode. Alias -d',
            'del': 'Delete the last exchange from memory',
            'forget': 'Forget the past conversation. Alias -f',
            'help': 'Display the list of commands',
            'his': 'The current conversation in memory. Alias history', 
            'log': 'Toggle to enable or disable logging of conversation + response times', 
            'read': 'Respond to text_prompt.txt', 
            'save': 'Save the recent prompt/response exchange to response.txt. Alias -s',
            'stats': 'Prints the current configuration and session total tokens.',
            'tanman': 'Bring up the TanManual (commands with their descriptions). Alias tan',
            'temp': 'Configure temperature (0.0-1.0)',
            'tok': 'Configure max tokens for the response',
            '-c': 'Respond to clipboard text (Uses conversation history)',
            '-rs': 'Amnesic clipboard summarizer',
            '-r': 'Versatile Amnesic Formatter, here is example usage:\n' +
                    'Case 1: `-r` => Uses clipboard as prompt, like -c\n' +
                    'Case 2: `-r is an example using a suffix!` => Replaces -r with contents of clipboard\n' +
                    'Case 3: `-r Analyze this url: -r Analysis:` => Replace "-r " with #clipboard_contents#\n'
            }