# TanTan
Conversational Chatbot + Speedy, (built-in) Reddit Media-Fetching

What it is and what it does:
- For now, there are separate components, the chatbot, the reddit fetcher, and the downloader, all continuing to be merged.
- Chatbot.py incorporates OpenAI's API, allowing access to different models, utilizing the combined power of ChatGPT's knowledge, DALL-E's image creation, reddit's existing content, and more, all without the need for a browser.
- The conversationality of chatbot.py is relatively rigid at the moment, but presets for different use cases, as well as better integration will soon be added.

Hi there! I'm new to creating tools for other people, and right now this is a cluttered mess, but as it comes together, I would love the feedback on aspects that don't feel natural. This work in progress is just for friends, but as it progresses, it's intended to be a more versatile tool to harness the power of AI and design neat browserless shortcuts to complete various tasks.

I have to decide whether I want this to be a program that lets you feel like a developer, changing the names around and having fun adding new functionality, or if I want to have established presets that just make it seem like something neat that someone made. I'm now leaning towards prioritizing making it accessible and not clunky to type in terminal each session. Built-in shortcuts app integration and the like, perhaps.

# Getting this onto your computer (MacOS only):
1. Go the the main github page @ github.com/TanGentleman/TanTan > Code > Download Zip
2. Download TanTan-Main (Should be in ~/Downloads)
3. Rename to TanTan and move the folder to the Desktop on your computer.
4. This location is the filepath variable in config.py
5. Move chat.py to your home directory instead, and ensure the filepath matches in chat.py and config.py
    - If you wish the install the repository anywhere else, just be sure to change it in these two files and you should be all good

Getting the Chatbot up and running from scratch (still in development):
Note that steps 1 and 2 require following the error message(s) and running the appropriate commands (like chmod for file permissions)
1. install homebrew
    - `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
2. install python
    - `brew install python`
If anything goes wrong before this point, let me know. Should be smooth sailing from here.
3. install dependencies
    - `pip3 install openai`
    - `pip3 install clipboard`
    - `pip3 install pillow`
    - `pip3 install requests`
5. Run chatbot from your home directory in terminal:
    - `python3 -i -m chat`

# Using the TanTan chatbot:
1. Paste your secret openai key to mysecrets.py
2. After completing the prerequisites above, and moving chat.py to your home directory:
    - `python3 -m -i chat`
    To see the manual of commands and descriptions:
    - `tan` or `tanman`
3. You're in! Have fun feeling like a computer whiz with the world of knowledge at your fintertips. 
- FYI: You can follow `python3 -m -i chat` with `config <engine> <max_tokens> <debug>`
- For instance `python3 -m -i chat config curie 30` for short, fast, simple responses with low latency.
- Or even ...`config codex` for a simple, default-token value codex response generator (great for basic function-making, needs basic prompt engineering)

- Please check out Chatbot/Chatbot_README.md for documentation and alternate setup environments. (Currently not too helpful)

*Advisory: I recommend using a VPN, especially when connected to public networks*
# Note: The below is entirely optional and not needed for chatbot.py. It will soon be integrated for cleaner workflows.

# Using MacOS Shortcuts to automate running reddit_fetcher.py and Downloader.py:
- Ask for Text with "Format: {u/user or r/subreddit} {qty} {new/top} {all/year/month/week/day/hour}"
- Run Shell Script
    - `python3 Desktop/TanTan/reddit_fetcher.py -s {PROVIDED_INPUT}`
- Text = Shell Script Result
- If <Text> <contains> <*shortcut_failure*>
    - Run this shortcut again (Link Grab + Download)
- Otherwise
    - Show Alert "Would you like to Download?"
    - Ask for Text with Folder Name:
    - Run Shell Script
    - `python3 Desktop/TanTan/Downloader.py {PROVIDED_INPUT}`
- End If

# Setting up the Reddit Image Fetcher:

(Pre-req: Create a reddit account)

Follow these steps to set up the Reddit Image Fetcher: 
1. Log in to your Reddit account and go to api prefs (https://www.reddit.com/prefs/apps).
2. Scroll down and create a new app with a name of your choice - this will be used as the user agent when filling out mysecrets.py later on. 
3. Select 'script' as the type of app, then leave the 'about url' blank and set redirect to http://localhost - this is just a dummy URL for now so you can move on with setup. 
4. Locate the client id (string of characters written next to an icon under 'personal use script') and client secret (string of characters written next to 'secret'). Copy these into their respective fields in mysecrets.py file, then set token_needed to True. Leave reddit_token as None for now - that's what we're trying to get!  
5. Double check that all required fields are entered correctly, then run test_setup by entering `python3 Desktop/TanTan/test_setup` into your terminal window - if it doesn't work let me know so I can help you troubleshoot! Hint: Make sure your repository is in the correct place, and you are running this terminal command from your *home directory*. The printed outcome value is reddit_token, you should enter that as a string into mysecrets.py accordingly before running functions from reddit_fetcher.py

# Running the Reddit Link Grabber:
1. Set the config.py variables filepath and reddit_folder_name
    - Filepath is where you installed this repository.
    - reddit_folder_name is a new folder that holds newly generated files
    - The other variables in config.py can be used in lieu of additional arguments in the command line
    - For now, please stick to subs/users with posts of standard image formats, not videos hosted elsewhere.
2. Set the 5 query variables in config.py, or add the Magic String in the command line for step 3.
- [MAGIC STRING] = {u/user or r/subreddit} {qty} {new/top} {all/year/month/week/day/hour} {-d for debug}
3. Run either command in terminal from your home directory.
    - `python3 Desktop/TanTan/reddit_fetcher.py`
    - `python3 Desktop/TanTan/reddit_fetcher.py r/houseplants 50 top year -d`
- This should generate a contents.txt file in the {reddit_folder_name} directory (TanTan/{reddit_folder_name})

# Downloading from contents.txt:
- The format in the file should be [Title + DELIMITER(something like '_||_' to separate them) + URL] for each entry
- The only argument following Downloader.py is the desired folder name.
1. Run command in terminal from your home directory.
    - `python3 Desktop/TanTan/Downloader.py Folder_For_Collected_Images`
- The above example would save the images to TanTan/{reddit_folder_name}/Folder_For_Collected_Images
