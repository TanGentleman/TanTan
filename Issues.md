Active Issues for chatbot:

[ x ] means fix being tested

Chatbot.py
- [ x ] ! Slow_Status fix to work within config argument strings.
- [ ] Find use case for completion_tokens, prompt_tokens vars
- [ x ] Find better way to handle log file not saved when error
- [ ] Make consistent the different ways of running it
- [ ] Consolidate codex + regular else condition logic into one function.

    - [ ] Move token_needed to mysecrets.py? Then one can fill that field and generate token there?
    - [ ] Or have a new file just for generating a token?

Reddit Link_Grabber
- [ x ] Enable video configuration with proper safeguards for large mp4 files and total download size.
- [ ] Enable YouTube downloads
- [ ] Fetch more meaningful data alongside the generated list


Fixed, but potentially unstable:
- Add generate token to mysecrets.py
- Logic for adding smart config strings like <config curie -d> or <config davinci 400> to the function interactive_chat()