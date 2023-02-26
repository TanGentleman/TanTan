# This OPTIONAL file should be moved to your Home directory! .../chat.py instead of .../Documents/TanTan/chatbot.py
# Allows running the chatbot in one simple line, with additional perks
# Instead of executing the file as a script, it imports chat.py as a module, allowing for the user to remain in the Python environment
# Permits arrow key functionality to see prior messages within an input() prompt, which can be an annoyance by default in the executable
    # The above perk needs readline installed, using homebrew make things simpler.


# Double check file is in ~/Users/{Name}/chat.py! and you are running this from {Name}! (Afaik, the default in terminal)
# Check Chatbot README.md for how to run

import sys
# Add our repository to our path, so the chatbot can be imported correctly.
sys.path.append('documents/github/tantan')
import chatbot

#set args
engine = 'dav'
tokens = '100'
args = ['python_env','config', engine, tokens]

#run 
chatbot.py_env_main(args)