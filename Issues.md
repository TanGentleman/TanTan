Under development:
- Tokenizer using an offline, local, pretrained GPT2 Model (Need to handle log-warning better)
- Documentation for the chatbot
- Documentation for the reddit scraper
- Integration between reddit scraping and chatbot
- Presets for chatbot. (i.e. debugging code, essay organization, fact checking, general advice)
- Image generation integration

[ x ] : fix being tested
# Active Issues:

Chatbot.py
- ![ ] Unsafe array accesses and variable assignments need to be handled appropriately
- ![ ] Add assert statements to ensure loop correctness
- [ ] Create better "help" functionality and prompt guidance
- [ ] Implement completion_tokens, prompt_tokens in their appropriate use cases
- [ x ] Find better way to handle log file not saved when error
- [ ] Make consistent the different ways of running it (i.e no downloads when loaded from python env.)
- [ ] Consolidate codex + regular else condition logic into one function.
- [ ] Need a way to cache history on user's request and later call it back smoothly.

Reddit Link_Grabber
- [ x ] Enable video configuration with proper safeguards for large mp4 files and total download size.
- [ ] Enable third-party (YouTube) downloads
- [ ] Fetch more meaningful data alongside the generated list

Fixed:
- Add generate token to test_setup.py
- Logic for adding smart config strings like <config curie -d> or <config davinci 400> to the function interactive_chat()
- Slow_Status needs to always apply, even if 'config arg' string shortcut used

To-Do List:
- Make var valid_flags = [-c, -cs, etc.] and organize command section accordingly
- Expand 'tanman' command to chatbot.py that shows full command list and better documentation

- Be able to save current convo to conversation.txt at any time.
- Create cache variables that can store engine/token/history values? 
    - It is possible that the better implementation is to create new engine/token/history variables, use them in generation,
    and only store in cache when needed, which should not be often.
- Work on better codex implementation
    - Text edit and text completions
- Comment and clean up functions in chatbot.py
- Add command to enable reddit downloading within chatbot session [ Under development ]
    - Allow calling Link_Grabber functions
    - Use prompt engineering on an OpenAI engine to generate magic strings from natural language and keywords
        - Create a dataset of natural language queries and corresponding magic strings [ In testing ]
- Work on image generation
- Play around with offline pretrained models like gpt2 but specialized

My current workflow for Chatbot:
- `python -i -m chat`

If message truncated:
- increase tokens as needed:
    - `tok`
    - input `500` (or however many ya need)

To complete a truncated response:
- Use a single space as the next input, should work fine with appropriate max token values.