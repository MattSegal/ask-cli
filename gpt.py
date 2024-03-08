import sys
import os

import anthropic
from openai import OpenAI
from rich import print
from rich.markup import escape
from rich.padding import Padding
from rich.progress import Progress

USE_ANTHROPIC = os.getenv("ANTHROPIC_API_KEY") or False

openai_client = OpenAI()

anthropic_client = None
if USE_ANTHROPIC:
    anthropic_client = anthropic.Anthropic()


class ClaudeModel:
    Opus = "claude-3-opus-20240229"
    Sonnet = "claude-3-sonnet-20240229"


class GPTModel:
    FourTurbo = "gpt-4-1106-preview"


ANTHROPIC_MODEL = ClaudeModel.Opus
GPT_MODEL = GPTModel.FourTurbo


def main(prompt: str):
    if not prompt:
        print("No prompt provided")
        return

    with Progress(transient=True) as progress:
        if USE_ANTHROPIC:
            progress.add_task("[red]Asking Claude 3...", start=False, total=None)
            try:
                answer_text = prompt_anthropic(prompt)
            except anthropic.InternalServerError:
                answer_text = "Request failed - Anthropic is broken"
        else:
            progress.add_task("[red]Asking GPT-4...", start=False, total=None)
            answer_text = prompt_gpt(prompt)

    answer = Padding(escape(answer_text), (2, 4))
    print(answer)


def prompt_anthropic(prompt: str):
    message = anthropic_client.messages.create(
        model=ANTHROPIC_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def prompt_gpt(prompt: str):
    chat_completion = openai_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}], model=GPT_MODEL
    )
    return chat_completion.choices[0].message.content


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:])
    main(prompt)
