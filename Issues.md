Current issue:
! Checks to see if directories valid first.
! Functions to make all needed folders
! Do reddit API key check before any workflow progress
! 

!! Issues in Downloader.py if filename arg invalid (like "r/sharks")
    - Should I just sanitize it first?

In development:
- Tokenizer using an offline, local, pretrained GPT2 Model (Need to handle log-warning better)
- Documentation for the chatbot
- Documentation for the reddit scraper
- Presets for chatbot. (i.e. debugging code, essay organization, fact checking, general advice, summarization, link analysis)
- Image generation integration
- Add command to enable reddit downloading within chatbot session [ In development ]
- Add command to enable image generation using DALL-E API

[ x ] : fix being tested
# Active Issues:

Chatbot.py
- [ ! ] Debug statements/variables that don't clutter, and have purpose.
- [ ! ] Unsafe array accesses and variable assignments need to be handled appropriately
- [ ] Checks to ensure loop correctness
- [ x ] Create better "help" functionality and prompt guidance
- [ ] Implement completion_tokens, prompt_tokens in their appropriate use cases


Reddit Link_Grabber
- [ x ] Enable video configuration with proper safeguards for large mp4 files and total download size.
- [ ] Enable third-party (YouTube) downloads
- [ ] Fetch more meaningful data alongside the generated list

# Inactive Issues:
- Consolidate codex + regular else condition logic
- Handle log file exceptions
- [ x ] Make consistent the different ways of running it (i.e no downloads when loaded from python env.)

Features Added:
- Add generate token to test_setup.py
- Logic for adding smart config strings like <config curie -d> or <config davinci 400> to the function interactive_chat()
- Add cache variables to store engine/token/history
- Expanded 'tanman' command documentation
- Be able to save current convo to conversation.txt at any time.

Bugs Squashed:
- Slow_Status needs to always apply, even if 'config arg' string shortcut used
- Pesky bugfix for empty string response not storing original prompt in history
- Filename from CLI arg sanitized in Downloader.py

To-Do List:
- Make var valid_flags = [-c, -cs, etc.] and organize command section accordingly

- Work on better codex implementation
    - Different OpenAI endpoints, like edits and embeddings
- Comment and clean up functions in chatbot.py [ In progress ]
- Add command to enable reddit downloading within chatbot session [ Under development ]
    - Allow calling Link_Grabber functions
    - Use prompt engineering on an OpenAI engine to generate magic strings from natural language and keywords
        - Create a dataset of natural language queries and corresponding magic strings [ In testing ]
- Work on image generation [ In development ]
- Play around with offline pretrained models like gpt2 but specialized [ In testing ]

My current workflow for Chatbot:
- `python -i -m chat`
- `config curie 20` Example config command, useful when testing

If message truncated:
- increase tokens as needed:
    - `tok`
    - input `500` (or whatever is adequate for your needs)

To complete a truncated response:
- Use a single space as the next input, should work fine with appropriate max token values.