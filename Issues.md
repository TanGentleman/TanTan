[ x ] : fix being tested
# Active Issues:

Chatbot.py
- [ ] Change some commands to flags (-c, -r, -rs, etc. to decrease collisions with legitimate prompts) + organize that section
- [ x ] Need safeguards in check_truncation_and_toks
- ![ ] Unsafe array accesses and variable assignments need to be handled appropriately
- ![ ] Add assert statements to ensure loop correctness
- [ ] Create better "help" functionality and prompt guidance
- [ ] Implement completion_tokens, prompt_tokens in their appropriate use cases
- [ x ] Find better way to handle log file not saved when error
- [ ] Make consistent the different ways of running it (i.e no downloads when loaded from python env.)
- [ ] Consolidate codex + regular else condition logic into one function.

Reddit Link_Grabber
- [ x ] Enable video configuration with proper safeguards for large mp4 files and total download size.
- [ ] Enable third-party (YouTube) downloads
- [ ] Fetch more meaningful data alongside the generated list

Fixed, but potentially unstable:
- Add generate token to test_setup.py
- Logic for adding smart config strings like <config curie -d> or <config davinci 400> to the function interactive_chat()
- Slow_Status needs to always apply, even if 'config arg' string shortcut used

Under development:
- Documentation for the chatbot
- Documentation for the reddit scraper
- Integration between reddit scraping and chatbot
- Presets for chatbot. (i.e. debugging code, essay organization, fact checking, general advice)
- Image generation integration

To-Do List:
- Create amnesic mode that doesn't keep track of convo
- Work on better codex implementation
    - Text edit and text completions
- Comment and clean up functions in chatbot.py
- Add command to enable reddit downloading within chatbot session [ Under development ]
    - Allow calling Link_Grabber functions
    - Use prompt engineering on an OpenAI engine to generate magic strings from natural language and keywords
        - Create a dataset of natural language queries and corresponding magic strings [ In testing ]
- Work on image generation
- Add 'tanman' command to chatbot.py that shows full command list and documentation [ Under development ]
