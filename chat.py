# This file should be moved to your home directory! .../chat.py instead of .../Documents/TanTan/chatbot.py
# Allows running the chatbot in one simple line, with additional perks
# Instead of executing the file as a script, it imports chat.py as a module, allowing for the user to remain in the Python environment

# Check Chatbot README.md for how to run

import sys
# Add our repository to our path, so the chatbot can be imported correctly.
sys.path.append('documents/tantan')
import chatbot

#set args
args = ['python_env']
if __name__ == '__main__':
    # Run the chatbot with the given args
    # If you want to run the chatbot with different args, change the args variable above
    # For example, to run the chatbot in debug mode, change args to ['python_env', '-d']
    # For more info, see the README.md in the chatbot folder
    args = ['python_env', 'config', 'davinci', '200']
    
chatbot.main_from_args(args)
