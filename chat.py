import sys
import os

# This OPTIONAL file can be duplicated and added to your Home directory! .../chat.py instead of .../Desktop/TanTan/chatbot.py
# This allows for running `python3 chat.py <args>` from your home directory.

# You are welcome to instead run chatbot.py from the repository folder

# This file is a wrapper for the chatbot, allowing for a simpler experience
# Allows both executing the file as a script, or importing chat.py as a module, so the user remains in the Python environment
# As needed down the line, this can be used to allow access to folders or files not in the repository

class TanTanSaysNo(Exception): pass # Make exception class TanTanSaysNo to be used in chat.py



# Add our repository to our path, so the chatbot can be imported correctly.

# This is the path to the repository, relative to your home directory.
FILEPATH = 'Desktop/Tantan'

# If user is already in the repository folder
if os.path.exists(os.path.join(os.getcwd(), 'config.py')):
    print("You are running chat.py from the repository folder. I'll find a way to make it work.")

else:
    filepath = FILEPATH
    sys.path.append(filepath) # Make sure to tweak this path! This is just where I keep the repository on my machine.
    from config import filepath as fp
    try:
        assert(filepath.lower() == fp.lower())
    except:
        raise TanTanSaysNo('Check that filepaths in chat.py and config.py match')


from chatbot import main_from_args as run_chatbot

def main():
    run_chatbot(sys.argv)


if __name__ == '__main__':
    main()
else:
    # default configuration for chatbot when used as a module
    args = ['python_env']
    run_chatbot(args)
