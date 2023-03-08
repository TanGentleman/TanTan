# New way to run the chatbot from within a python environment:
1. Move chat.py to your home directory and configure FILENAME.
2. Run terminal command:
- `python3 chat.py`

# Type `tan` to see the current list of commands

# Options to run the Chatbot
Recommended:
Option 1. From the home directory, type `python3 chat.py` in terminal 
        (You can follow 'chat.py' with an optional config string to launch a specific configuration)
        (Filepath in chat.py AND config.py must be correct)


Option 2. From the repository directory (TanTan), type `python3 chatbot.py`
Option 3. From home, type `python3 path/to/chatbot.py` (Filepath in config.py must be correct)

# Simplify the workflow!
MacOS Shortcuts:
Create a new shortcut with a name of your choice, 'Launch Chatbot' for instance. The body will only have one command.
1. Run Shell script:
```osascript -e 'tell application "Terminal" to do script "python3 Desktop/TanTan/chatbot.py" activate'```
# To run:
- Run Launch Chatbot
- That's it!!
