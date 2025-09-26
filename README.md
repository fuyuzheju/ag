# AI for terminal

Chat with AI in your **terminal**!
`Stream` output is supported, just like in your web browser.
Both brief question and long session are supported.
Renders `MARKDOWN` with *glow*.

# Install
1. Install glow(to render markdown)
```bash
# macos
brew install glow

# ubuntu
apt install glow

# ...
```

2. Build env
```bash
pip install -r requirements.txt
```
And then put your API Key of gemini in `.env` as an environmental variable

3. Run script
```bash
python ag.py
```

# Usage
- Basic
> If you use `ag` with no arguments, it automatically enters the interactive mode, where you can have a long session with AI
> If you use `ag [prompt]`, it will print out the model's response, but you will not be able to ask follow-up questions, and the context will not be preserved

- -g
> beautify the output with **glow**

- -m
> set the AI model. default as gemini-2.5-flash

