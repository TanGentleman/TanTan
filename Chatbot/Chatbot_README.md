# Chatbot Documentation:
- Work in Progress.


Workaround to run from within a python environment:
- `cd`
- `python3`
- `import sys`
- `sys.path.append('/path/to/TanTan')`
- `import chatbot`
- `args = ['python_env', 'config', 'ada', '24']`
- `chatbot.main2(args)`

New way to run the chatbot from within a python environment:
1. Move chat.py to your home directory and configure default.
2. Run terminal command:
- `python -i -m chat`

# Shortcuts:
1. [Text]:python -i -m chat
2. Copy [Text] to clipboard
3. Open Terminal

# To run:
- Run shortcut
- Paste and hit return, violá
- To relaunch from python environment after quitting, simply type `import chat`
