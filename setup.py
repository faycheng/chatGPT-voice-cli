from setuptools import find_packages
from setuptools import setup

setup(
    name="chatbot_cli",
    version="0.0.1",
    license="MIT License",
    author="Fay Cheng",
    author_email="fay.cheng.cn@gmail.com",
    description="chatGPT-bot is a voice assistant using the OpenAI's ChatGPT API",
    packages=find_packages("pkg"),
    package_dir={"": "pkg"},
    py_modules=["chatbot_cli", "chatgpt", "conf", "speech_recognition"],
    url="https://github.com/faycheng/chatGPT-voice-cli",
    install_requires=[
        "openai",
        "tiktoken",
        "prompt_toolkit",
        "fire",
        "azure-cognitiveservices-speech",
        "dynaconf"
    ],
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    entry_points={
        "console_scripts": [
            "chatGPT-voice=chatbot_cli:main",
        ],
    },
)

