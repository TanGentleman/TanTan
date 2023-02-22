# TanTan
OpenAI Chatbot with Reddit Scraping Functionality

Hi there! I'm new to creating tools for other people, so if anything seems counterintuitive, you're likely not alone and I would love the feedback on aspects that don't feel natural.

I've built this primarily for:
- People who enjoy the shortcut to reddit scraping or find the Chatbot cool/useful 
- Anyone who'd like to play around with code and build upon a project I've had a ton of fun making.

I have to decide whether I want this to be a program that lets you feel like a developer, changing the names around and having fun adding new functionality, or if I want to have established presets that just make it seem like something neat that someone made.

# Steps to Dependencies:
1. Download the latest python version from the official website: https://www.python.org/downloads/
2. Type python3 in terminal
3. Install required command line tools if needed
4. Install the required libraries in terminal using pip (Python package manager):
    - `pip install openai`

*Strong avisory: I recommend using a VPN when using the internet, especially over unsecure networks*

The following steps assume you have all the required dependencies. Should I make a formal check for this?
How to use the Reddit Scraper:

(Pre-req: Create a reddit account)

1. Locate your Reddit username and password
2. Go to api prefs (https://www.reddit.com/prefs/apps), and log in
3. (Near the bottom) Create another app 
4. Set name to whatever you'd like, this will be your user agent when filling out mysecrets.py
5. Select script (Not web app or installed app)
6. Description: (What it does - i.e. "Scrapes")
7. You can leave about url blank, and set redirect to a dummy url: http://localhost should do fine.
8. Locate the client id: String of characters written to the right of the icon under personal use script
9. Locate the client secret: String of characters written next to 'secret'
10. You should be all done using your browser! Paste these into their respective fields in mysecrets.py
11. Run mysecrets.py and note the printed string. This is reddit_token, please set it accordingly
12. You're all done with the essentials to run the scraper! Please try running test_setup.py (In progress)


# Running the Reddit Scraper:
1. Set the config.py variables filepath and reddit_folder_name
- Filepath is where you installed this repository.
- reddit_folder_name is a new folder that holds newly generated files
- The other variables in config.py can be used in lieu of additional arguments in the command line
- For now, please stick to subs/users with posts of standard image formats, not videos hosted elsewhere.
- [MAGIC STRING] = {u/user or r/subreddit} {qty} {new/top} {all/year/month/week/day/hour} {-d for debug}
    - `python3 Documents/TanTan/Link_Grabber.py`
    - `python3 Documents/TanTan/Link_Grabber.py r/houseplants 50 top year -d`
- This should generate a contents.txt file in the {reddit_folder_name} directory (Documents/TanTan/{reddit_folder_name})

# Downloading from contents.txt:
- The format in the file should be [Title + DELIMITER(something like '_||_' to separate them) + URL] for each entry
- The only argument following Downloader.py is the desired folder name.
    - `python3 Documents/TanTan/Downloader.py Folder_For_Collected_Images`

How to use the TanTan chatbot
(Pre-req: Create an openai account)
1. Grab your openai api key from (https://platform.openai.com/account/api-keys)
2. Paste this key to mysecrets.py
    - `python3 Documents/TanTan/Chatbot.py`

List of important variables, functions, and workflows (Work in Progress):
- 

*Should I make a separate markdown file for this?*
