# This OPTIONAL file should be moved to your Home directory! .../chat.py instead of .../Desktop/TanTan/chatbot.py
# If you would like to run the chatbot without this file, type instead `python3 path/to/chatbot.py` in terminal

# This file is a wrapper for the chatbot, allowing for a more user-friendly experience
# Run chatbot in one simple line `python3 -i -m chat`, with additional perks too!
# Instead of executing the file as a script, it imports chat.py as a module, allowing for the user to remain in the Python environment
# Permits arrow key functionality to see prior messages within an input() prompt, which can be an annoyance by default in the executable
    # The above perk needs readline installed, using homebrew make things simpler.


# Double check file is in ~/Users/{Name}/chat.py! and you are running this from {Name}! (Afaik, the default in terminal)
# Check Chatbot README.md for troubleshooting

import sys
# Add our repository to our path, so the chatbot can be imported correctly.

# This is the path to the repository, relative to your home directory.
filepath = 'Desktop/Tantan'

sys.path.append(filepath) # Make sure to tweak this path! This is just where I keep the repository on my machine.

import chatbot
from config import filepath as fp

# Make exception class TanTanSaysNo to be used in chat.py
class TanTanSaysNo(Exception):
    pass

try:
    assert(filepath == fp)
except:
    raise TanTanSaysNo('Check that filepaths in chat.py and config.py match')

def main():
    chatbot.main_from_args(sys.argv)


if __name__ == '__main__':
    main()
else:
    # default configuration for chatbot when used as a module
    args = ['python_env']
    chatbot.main_from_args(args)
