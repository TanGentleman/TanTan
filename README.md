# TanTan
Conversational Chatbot + Speedy, (built-in) Reddit Media-Fetching

What it is and what it does:
- For now, there are two separate components, the chatbot, and reddit scraper, soon to be merged.
- Using chatbot.py incorporates OpenAI's API to use their different models, utilizing the combined power of ChatGPT's knowledge, DALL-E's image creation, reddit's existing content, and more, all without the need for a browser.
- The conversationality of chatbot.py is relatively rigid at the moment, but presets for different use cases, as well as better integration will soon be added.

In Progress:
- Documentation for using chatbot.py
- Documentation for using link_grabber.py and downloader.py
- Better checks for valid filepaths
- MacOS Shortcuts Integration

Hi there! I'm new to creating tools for other people, and right now this is a cluttered mess, but as it comes together, I would love the feedback on aspects that don't feel natural. This rough work in progress is just for friends, but as it progresses, it's intended to be a more versatile tool to harness ChatGPT's engines and design neat browserless shortcuts to complete various tasks.

I have to decide whether I want this to be a program that lets you feel like a developer, changing the names around and having fun adding new functionality, or if I want to have established presets that just make it seem like something neat that someone made. I'm now leaning towards prioritizing making it accessible and not clunky to type in terminal each session. Built-in shortcuts app integration and the like, perhaps.

Some of the goals of this project are to be able to do the following:

Workflow 1:
1. Select some text anywhere on your computer 
2. Use a keyboard shortcut to call the TT Chatbot.
3. * Request that the text be more clearly explained, with a glossary of important words and phrases at the bottom
4. Clarify further questions and maintain a full conversation, saving any desired output in a friendly format.

* = Any manipulation of the text can go here.

At the moment, this is super rough, not user friendly, and tricky to troubleshoot new features. I want to fix this, but thought it'd be neat if all the functions could be reorganized by the chatbot itself. Creating comments and optimizing for clarity of each function's role will be the assigned task. Over time, most of the core code should get cleaned up by davinci if a suitable workflow can be made. An example would be starting the chatbot, typing `codex`, pasting some functions into codex_prompt.txt, and getting a good response that also saves to codex_response.txt.

# Getting this onto your computer (MacOS only):
1. Go the the github page > Code > Download Zip
2. Download TanTan-Main
3. Rename to TanTan and move to ~/Documents on your computer.
4. This location is the filepath variable in config.py

# Steps to Load Dependencies:
1. Download the latest python version from the official website: https://www.python.org/downloads/
2. Type python3 in terminal
3. Install required command line tools if needed
4. Install pip (Python package manager) if needed:
    - `cd`
    - `curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py`
    - `python get-pip.py`
    - If you get an error saying WARNING: The scripts pip... are installed in '<.../bin>' which is not on PATH, you have to add it to path
        - For that, copy what was written in '<>', adding a /pip3 to it 
        - This will look something like 'Users/.../Library/Python/3.9/bin/pip3'
        - Paste that instead of MUFFIN below
    - `sudo set PATH=%PATH%'MUFFIN'`

4. Install the required libraries in terminal using pip:
    - `pip3 install requests`
    - `pip3 install openai` (if using chatbot)
    

- You should be all set up with the dependencies!

*Strong avisory: I recommend using a VPN when using the internet, especially over unsecure networks*

The following steps assume you have all the required dependencies. (Should I make a formal check for this?)

# Using the TanTan chatbot:
(Pre-req: Create an openai account)
1. Grab your openai api key from (https://platform.openai.com/account/api-keys)
2. Paste this key to mysecrets.py
    - `cd`
    - `python3 Documents/TanTan/Chatbot.py`

- I have yet to make proper documentation for the chatbot. For now, play around with asking it stuff.
- Ada, Babbage, Curie, and Davinci are 4 engines that vary in their capabilities
- There is also a code-davinci that I have included as "codex"
- Type help as a prompt to get some of the commands
    - I have yet to make this even remotely user friendly.

# Setting up the Reddit Image Fetcher:

(Pre-req: Create a reddit account)

1. Locate your Reddit username and password
2. Go to api prefs (https://www.reddit.com/prefs/apps), and log in
3. (Near the bottom) Create another app 
4. Set name to whatever you'd like, this will be your user agent when filling out mysecrets.py
5. Select script (Not web app or installed app)
6. Description: (What it does - i.e. "Fetches")
7. You can leave about url blank, and set redirect to a dummy url: http://localhost should do fine.
8. Locate the client id: String of characters written to the right of the icon under personal use script
9. Locate the client secret: String of characters written next to 'secret'
10. You should be all done using your browser! Paste these into their respective fields in mysecrets.py
11. Set token_needed to True, and leave reddit_token as None for now.
12. Triple check that all the required fields are entered correctly.
13. Run test_setup.py with the below command and note the printed string. This is reddit_token, please set it accordingly
    - `python3 Documents/TanTan/test_setup.py`
    - If this does not work, please let me know, I am working on some better safeguards.
    - This printed value is reddit_token, please set it accordingly in mysecrets.py
14. You're all done with the essentials! You should now be able to run Link_Grabber.py and Downloader.py

# Running the Reddit Link Grabber:
1. Set the config.py variables filepath and reddit_folder_name
    - Filepath is where you installed this repository.
    - reddit_folder_name is a new folder that holds newly generated files
    - The other variables in config.py can be used in lieu of additional arguments in the command line
    - For now, please stick to subs/users with posts of standard image formats, not videos hosted elsewhere.
2. Set the 5 query variables in config.py, or add the Magic String in the command line for step 3.
- [MAGIC STRING] = {u/user or r/subreddit} {qty} {new/top} {all/year/month/week/day/hour} {-d for debug}
3. Run the command in terminal from your home directory.
    - `cd`
    - `python3 Documents/TanTan/Link_Grabber.py`
    - `python3 Documents/TanTan/Link_Grabber.py r/houseplants 50 top year -d`
- This should generate a contents.txt file in the {reddit_folder_name} directory (Documents/TanTan/{reddit_folder_name})

# Downloading from contents.txt:
- The format in the file should be [Title + DELIMITER(something like '_||_' to separate them) + URL] for each entry
- The only argument following Downloader.py is the desired folder name.
    - `cd`
    - `python3 Documents/TanTan/Downloader.py Folder_For_Collected_Images`
- The above example would save the images to TanTan/{reddit_folder_name}/Folder_For_Collected_Images


List of important variables, functions, and workflows (Work in Progress):
- 

*Should I make a separate markdown file for this?*
