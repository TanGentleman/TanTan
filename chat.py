# This OPTIONAL file should be moved to your Home directory! .../chat.py instead of .../Documents/TanTan/chatbot.py
# Allows running the chatbot in one simple line, with additional perks
# Instead of executing the file as a script, it imports chat.py as a module, allowing for the user to remain in the Python environment
# Permits arrow key functionality to see prior messages within an input() prompt, which can be an annoyance by default in the executable
    # The above perk needs readline installed, using homebrew make things simpler.


# Double check file is in ~/Users/{Name}/chat.py! and you are running this from {Name}! (Afaik, the default in terminal)
# Check Chatbot README.md for how to run

import sys
# Add our repository to our path, so the chatbot can be imported correctly.

sys.path.append('Desktop/Tantan') # Make sure to tweak this path! This is just where I keep the repository on my machine.

import chatbot

if __name__ == '__main__':
    chatbot.main_from_args(sys.argv)
else:
    # default configuration for chatbot when used as a module
    args = ['python_env']
    chatbot.main_from_args(args)
