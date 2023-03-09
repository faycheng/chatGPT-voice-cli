# ChatGPT Voice CLI
A command line tool for having voice conversations with ChatGPT.

## Features
- Record voice input and submit it to ChatGPT
- Read responses aloud

## Commands
- `chatGPT-voice text_conversation`: Have a text conversation with ChatGPT, and read the responses aloud
- `chatGPT-voice voice_conversation`: Have a voice conversation with ChatGPT, in this mode, the tool would recognize your speaking and submit it to ChatGPT, then, read responses for you

## Installation
1. Clone the repository: `git clone https://github.com/faycheng/chatGPT-voice-cli`
2. Change to the project directory: `cd chatGPT-voice-cli`
3. Install the package: `python setup.py install`
4. Set your OpenAI and Azure credentials:
```
export CHAT_OPENAI_KEY={YOUR_OPEN_AI_KEY}
export CHAT_AZURE_REGION={YOUR_AZURE_REGION}
export CHAT_AZURE_KEY={YOUR_AZURE_KEY}
```


## Usage
After installation, you can use the `chatGPT-voice` command to start a voice or text conversation with ChatGPT. Follow the prompt to select the mode of conversation.

## Requirements
- Python 3.6 or higher
- OpenAI API Key
- Azure Speech to Text API Key and Region

## License
This project is licensed under the terms of the MIT license.
