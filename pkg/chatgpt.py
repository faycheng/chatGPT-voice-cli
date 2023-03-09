
import openai

import tiktoken

from conf import settings


def num_tokens_from_string(string: str, encoding_name="cl100k_base") -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


class ChatBot(object):
    def __init__(self):
        self.histories = []

    def construct_prompt_messages(self, prompt):
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
        ]
        for history in self.histories:
            messages.append(history)
        messages.append({"role": "user", "content": prompt})
        return messages

    def ask(self, prompt):
        def num_tokens_from_messages(messages):
            token = 0
            for message in messages:
                token += num_tokens_from_string(message['content'])
            return token
        messages = self.construct_prompt_messages(prompt)
        cur_token = num_tokens_from_messages(messages)
        if cur_token > 4096:
            # todo: drop some messages
            raise Exception("the length of the prompt is too long to process")
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.3,
            max_tokens=4000-cur_token,
            stream=True,
        )
        self.histories.append(messages[-1])
        self.histories.append({"role": "assistant", "content": ""})
        for message in completion:
            if 'content' not in message['choices'][0]['delta']:
                continue
            text = message['choices'][0]['delta']['content']
            self.histories[-1]['content'] += text
            yield text




