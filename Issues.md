# Active Issues (Priority L/M/!):
- [ ! ] Unsafe array accesses and possible errors need to be handled appropriately
- [ ! ] Add command to enable reddit downloading within chatbot session
- [ ! ] Explicit typing and function descriptions for all functions (chatbot.py should be good)
- [ L ] Debug print statements that don't clutter, and have purpose.
- [ L ] Documentation for the reddit scraper
- [ M ] Documentation for the chatbot
- [ M ] Presets for chatbot. (i.e. debugging code, essay organization, fact checking, general advice, summarization, link analysis)
- [ L ] Implement completion_tokens, prompt_tokens in their appropriate use cases

 
- Tokenizer using an offline, local, pretrained GPT2 Model (Still a dev command)
    - Also want to run some tests to see if computation is expensive enough to warrant this disabled by default.

- Add command to enable reddit downloading within chatbot session [ In development ]

[ x ] : fix being tested

[ x ] Checks to see if directories valid first.
! Functions to make all needed folders
! Do reddit API key check before any workflow progress
!! Make a datatype that holds engine configuration (Should it be passed slow_status?)

Chatbot.py
- [ ! ] Debug statements/variables that don't clutter, and have purpose.

- [ ] Checks to ensure loop correctness
- [ x ] Create better "help" functionality and prompt guidance
- [ ] Implement completion_tokens, prompt_tokens in their appropriate use cases



reddit_fetcher.py
- [ x ] Enable video configuration with proper safeguards for large mp4 files and total download size.
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
- Image generation fully live using -images
- YouTube download from url in clipboard fully live using -yt
- 


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
- Play around with offline pretrained models like gpt2 but specialized [ In testing ]


If message truncated:
- increase tokens as needed:
    - `tok`
    - input `500` (or whatever is adequate for your needs)



# Legacy (no longer applicable):

To complete a truncated response:
- Use a single space as the next input, should work fine with appropriate max token values.
