# Active Issues (Priority L/M/!):
- [ ! ] Unsafe array accesses and possible errors need to be handled appropriately
- [ L ] Add command to enable reddit downloading within chatbot session
- [ ! ] Explicit typing and function descriptions for all functions (chatbot.py should be good)
- [ L ] Debug print statements that don't clutter, and have purpose.
- [ L ] Documentation for the reddit scraper
- [ M ] Documentation for the chatbot
- [ M ] Presets for chatbot. (i.e. debugging code, essay organization, fact checking, general advice, summarization, link analysis)
- [ L ] Implement completion_tokens, prompt_tokens in their appropriate use cases
- [ ! ] Go back over non-chatbot files for safety and documentation
- [ L ] Make better use of the reddit api, reddit_fetcher.py can be far more powerful
- [ L ] Utilize other OpenAI endpoints: edits and text embeddings, as well as moderation endpoint for some use cases

Currently still dev-only:
- transformers library for dev variable in config.py (Enables -len and check_length var to show how many tokens your prompt has)
- This is a tokenizer using an offline, local, pretrained GPT2 Model
    - I would like to run some tests to see if computation is expensive enough to warrant this disabled by default.
    - I am currently leaning towards transformers being one of the very easy to install optional libraries alongside pytube

Features Added:
- Logic for adding smart config strings like <config curie -d> or <config davinci 400> to the function interactive_chat()
- Utilize cache variables to store current engine/token/history
- Expanded 'tanman' command documentation
- Be able to save current convo to conversation.txt at any time.
- Escape string 'quit' can be used in any input() call, and it saves whenever possible
- Commands now integrate copy and paste functionality, allowing for efficient workflows (deals with potentially annoying spaces or newlines)
- Image generation fully live using -images
- chat.py serves a purpose, will be more useful if folders needed to be accessed outside repository.
- Magic string generation
- YouTube download from url in clipboard fully live using -yt
- 


Bugs Squashed:
- Slow_Status needs to always apply, even if 'config arg' string shortcut used
- Pesky bugfix for empty string response not storing original prompt in history
- Filename from CLI arg sanitized in Downloader.py
- Empty string response dealt with (Changed response string to same delimiter as logs)
- A million others that if I handled correctly, you will never notice :)

# Legacy (no longer applicable):
- Magic string generation using text file from the training set (Will re-integrate eventually)
