Current issue:
- Clarify engine types and allow friendly choosing using config strings

In development:
- A more readable README

- Tokenizer using an offline, local, pretrained GPT2 Model (Need to handle log-warning better)
    - Also want to run some tests to see of computation ends up being a limiting factor, I should be able run it in parallel with response generation in the existing code if needbe.
- Documentation for the chatbot
- Documentation for the reddit scraper
- Presets for chatbot. (i.e. debugging code, essay organization, fact checking, general advice, summarization, link analysis)
- Image generation integration
- Add command to enable reddit downloading within chatbot session [ In development ]
- Add command to enable image generation using DALL-E API

[ x ] : fix being tested
# Active Issues:
[ x ] Checks to see if directories valid first.
! Functions to make all needed folders
! Do reddit API key check before any workflow progress
!! Make a datatype that holds engine configuration (Should it be passed slow_status?)

Chatbot.py
- [ ! ] Debug statements/variables that don't clutter, and have purpose.
- [ ! ] Unsafe array accesses and variable assignments need to be handled appropriately
- [ ] Checks to ensure loop correctness
- [ x ] Create better "help" functionality and prompt guidance
- [ ] Implement completion_tokens, prompt_tokens in their appropriate use cases



reddit_fetcher.py
- [ x ] Enable video configuration with proper safeguards for large mp4 files and total download size.
- [ ] Enable third-party (YouTube) downloads
- [ ] Fetch more meaningful data alongside the generated list

# Inactive Issues:
- Consolidate codex + regular else condition logic
- Handle log file exceptions
- [ x ] Make consistent the different ways of running it (i.e no downloads when loaded from python env.)
- Work on better codex implementation
- Make all non-responses “continue” in the while loop.

Features Added:
- Add generate token to test_setup.py
- Logic for adding smart config strings like <config curie -d> or <config davinci 400> to the function interactive_chat()
- Add cache variables to store current engine/token/history
- Expanded 'tanman' command documentation
- Be able to save current convo to conversation.txt at any time.
- Escape string 'quit' can be used in any input() call, and it saves whenever possible
- Tidy up clipboard manipulation, allowing for powerful use in copying and pasting, without spaces or newlines being annoying


Bugs Squashed:
- Slow_Status needs to always apply, even if 'config arg' string shortcut used
- Pesky bugfix for empty string response not storing original prompt in history
- Filename from CLI arg sanitized in Downloader.py
- Empty string response not handled currectly (Changed response string to same delimiter as logs)

To-Do List:
- The else condition will be the only one that directly calls generate_text, and exits the clause when the response string obtained.
- Body of interactive_chat will report that response is True

- Other OpenAI endpoints: edits and text embeddings, as well as moderation endpoint
- Comment and clean up functions in chatbot.py [ In progress ]
- Add command to enable reddit downloading within chatbot session [ Under development ]
    - Allow calling reddit_fetcher functions
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