# Ask CLI

```
❯ ask --help

Usage: ask [OPTIONS] COMMAND [ARGS]...

  Ask your language model a question.

  Examples:
    ask how do I flatten a list in python
    ask ffmpeg convert webm to a gif
    ask what is the best restaurant in melbourne?
    echo 'hello world' | ask what does this text say
    ask web http://example.com | ask what does this website say

Options:
  --help  Show this message and exit.

Commands:
  <default>  Simple one-off queries with no chat history
  chat       Continue chat after initial ask
  config     Set up or configure this tool
  img        Render an image with DALLE-3
  web        Scrape content from provided URLs (HTML, PDFs)
```

Note: GIF is out of date

![](./gpt.gif)

## Global setup

Get access to binary everywhere

```bash
# Build the wheel
python -m venv venv
. ./venv/bin/activate
pip install poetry
poetry build
deactivate

# Install with pipx
brew install pipx
pipx install dist/*.whl
```

## Dev setup

Install project requirements:

```bash
python -m venv venv
. ./venv/bin/activate
pip install poetry
poetry install
ask --help
ask config
```
