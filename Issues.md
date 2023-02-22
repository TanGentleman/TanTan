Under development:
- Image generation integration

Active Issues:

[ x ] : fix being tested

Chatbot.py
- ![ ] Need safeguards in check_truncation_and_toks
- ![ ] Unsafe array accesses and variable assignments need to be handled appropriately
- ![ ] Add assert statements to ensure loop correctness
- [ x ] Slow_Status needs to always apply, even if 'config arg' string shortcut used
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