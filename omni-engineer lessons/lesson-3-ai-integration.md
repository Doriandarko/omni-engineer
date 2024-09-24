# Lesson 3: Integrating AI Capabilities

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Setting up OpenAI API](#openai-setup)
4. [Creating an AI Client](#ai-client)
5. [Implementing Basic AI Responses](#basic-responses)
6. [Handling Streaming Responses](#streaming-responses)
7. [Adding AI Commands](#ai-commands)
8. [Error Handling and Retries](#error-handling)
9. [Conclusion](#conclusion)

<a name="introduction"></a>
## 1. Introduction

In this lesson, we'll focus on integrating AI capabilities into our CLI tool using the OpenAI API. We'll create an AI client, implement both basic and streaming responses, add AI-specific commands, and handle errors and retries. By the end of this lesson, your CLI tool will be able to interact with an AI model, providing intelligent responses to user queries.

<a name="project-structure"></a>
## 2. Project Structure

Let's update our project structure to accommodate the new AI-related features:

```
ai_cli_tool/
│
├── ai_cli_tool/
│   ├── __init__.py
│   ├── main.py
│   ├── cli.py
│   ├── commands/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── help.py
│   │   ├── exit.py
│   │   ├── ask.py         # New file for AI query command
│   │   └── chat.py        # New file for AI chat command
│   ├── ai_integration/
│   │   ├── __init__.py
│   │   ├── client.py      # New file for AI client
│   │   └── models.py      # New file for AI model configurations
│   ├── file_handler.py
│   ├── utils.py
│   └── config.py
│
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_commands.py
│   ├── test_ai_integration.py
│   ├── test_file_handler.py
│   └── test_utils.py
│
├── .env
├── requirements.txt
├── setup.py
└── README.md
```

<a name="openai-setup"></a>
## 3. Setting up OpenAI API

First, make sure you have an OpenAI API key. If you don't have one, sign up at https://openai.com/ and create an API key.

Update your `.env` file to include your OpenAI API key:

```
OPENAI_API_KEY=your_api_key_here
```

Next, update the `requirements.txt` file to include the OpenAI library:

```
click==8.1.3
openai==0.27.0
python-dotenv==0.19.2
colorama==0.4.4
prompt_toolkit==3.0.28
aiohttp==3.8.3  # For asynchronous HTTP requests
```

<a name="ai-client"></a>
## 4. Creating an AI Client

Let's create an AI client that will handle communication with the OpenAI API. Create a new file `ai_cli_tool/ai_integration/client.py`:

```python
# ai_cli_tool/ai_integration/client.py

import openai
import asyncio
import aiohttp
from ..config import OPENAI_API_KEY
from .models import AI_MODELS

class AIClient:
    def __init__(self):
        openai.api_key = OPENAI_API_KEY
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.close()

    async def get_response(self, prompt, model="gpt-3.5-turbo", max_tokens=150):
        try:
            response = await openai.ChatCompletion.acreate(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except openai.error.OpenAIError as e:
            raise AIClientError(f"Error in AI response: {str(e)}")

    async def get_streaming_response(self, prompt, model="gpt-3.5-turbo", max_tokens=150):
        async for chunk in await openai.ChatCompletion.acreate(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            stream=True,
        ):
            content = chunk["choices"][0].get("delta", {}).get("content")
            if content is not None:
                yield content

class AIClientError(Exception):
    pass
```

Now, let's create a file for AI model configurations. Create `ai_cli_tool/ai_integration/models.py`:

```python
# ai_cli_tool/ai_integration/models.py

AI_MODELS = {
    "gpt-3.5-turbo": {
        "name": "GPT-3.5 Turbo",
        "max_tokens": 4096,
        "description": "Most capable GPT-3.5 model and optimized for chat at 1/10th the cost of text-davinci-003."
    },
    "gpt-4": {
        "name": "GPT-4",
        "max_tokens": 8192,
        "description": "More capable than any GPT-3.5 model, able to do more complex tasks, and optimized for chat."
    },
}

DEFAULT_MODEL = "gpt-3.5-turbo"
```

<a name="basic-responses"></a>
## 5. Implementing Basic AI Responses

Now that we have our AI client set up, let's implement a basic AI response command. Create a new file `ai_cli_tool/commands/ask.py`:

```python
# ai_cli_tool/commands/ask.py

import asyncio
from .base import BaseCommand
from ..ai_integration.client import AIClient, AIClientError
from ..utils import print_colored

class AskCommand(BaseCommand):
    @classmethod
    def name(cls):
        return "ask"

    @classmethod
    def description(cls):
        return "Ask the AI assistant a question"

    async def execute(self, args):
        prompt = " ".join(args[1:])
        if not prompt:
            print_colored("Please provide a question to ask the AI.", "yellow")
            return

        print_colored("Thinking...", "cyan")
        try:
            async with AIClient() as client:
                response = await client.get_response(prompt)
            print_colored("AI response:", "green")
            print(response)
        except AIClientError as e:
            print_colored(str(e), "red")

    def execute(self, args):
        asyncio.run(self.execute_async(args))
```

Update the `ai_cli_tool/commands/__init__.py` file to include the new command:

```python
# ai_cli_tool/commands/__init__.py

from .help import HelpCommand
from .exit import ExitCommand
from .ask import AskCommand

def get_command(command_name):
    commands = {cmd.name(): cmd for cmd in get_all_commands()}
    return commands.get(command_name.split()[0].lower())()

def get_all_commands():
    return [HelpCommand, ExitCommand, AskCommand]
```

<a name="streaming-responses"></a>
## 6. Handling Streaming Responses

To provide a more interactive experience, let's implement a chat command that uses streaming responses. Create a new file `ai_cli_tool/commands/chat.py`:

```python
# ai_cli_tool/commands/chat.py

import asyncio
from .base import BaseCommand
from ..ai_integration.client import AIClient, AIClientError
from ..utils import print_colored

class ChatCommand(BaseCommand):
    @classmethod
    def name(cls):
        return "chat"

    @classmethod
    def description(cls):
        return "Start a chat session with the AI assistant"

    async def execute_async(self, args):
        print_colored("Starting chat session. Type 'exit' to end the chat.", "cyan")
        async with AIClient() as client:
            while True:
                user_input = input("You: ")
                if user_input.lower() == 'exit':
                    break

                print_colored("AI: ", "green", end="")
                try:
                    async for chunk in client.get_streaming_response(user_input):
                        print(chunk, end="", flush=True)
                    print()  # New line after response
                except AIClientError as e:
                    print_colored(str(e), "red")

        print_colored("Chat session ended.", "cyan")

    def execute(self, args):
        asyncio.run(self.execute_async(args))
```

Don't forget to update the `ai_cli_tool/commands/__init__.py` file to include the new chat command.

<a name="ai-commands"></a>
## 7. Adding AI Commands

Now that we have our basic AI interactions set up, let's add some more advanced AI-powered commands. For example, we can create a command that generates code based on a description. Create a new file `ai_cli_tool/commands/generate_code.py`:

```python
# ai_cli_tool/commands/generate_code.py

import asyncio
from .base import BaseCommand
from ..ai_integration.client import AIClient, AIClientError
from ..utils import print_colored

class GenerateCodeCommand(BaseCommand):
    @classmethod
    def name(cls):
        return "generate_code"

    @classmethod
    def description(cls):
        return "Generate code based on a description"

    async def execute_async(self, args):
        description = " ".join(args[1:])
        if not description:
            print_colored("Please provide a description of the code you want to generate.", "yellow")
            return

        prompt = f"Generate Python code for the following description: {description}"
        
        print_colored("Generating code...", "cyan")
        try:
            async with AIClient() as client:
                response = await client.get_response(prompt, max_tokens=500)
            print_colored("Generated code:", "green")
            print(response)
        except AIClientError as e:
            print_colored(str(e), "red")

    def execute(self, args):
        asyncio.run(self.execute_async(args))
```

Remember to update the `ai_cli_tool/commands/__init__.py` file to include this new command.

<a name="error-handling"></a>
## 8. Error Handling and Retries

To make our AI integration more robust, let's implement error handling and retries. Update the `ai_cli_tool/ai_integration/client.py` file:

```python
# ai_cli_tool/ai_integration/client.py

import openai
import asyncio
import aiohttp
from ..config import OPENAI_API_KEY
from .models import AI_MODELS

class AIClient:
    def __init__(self, max_retries=3, retry_delay=1):
        openai.api_key = OPENAI_API_KEY
        self.session = None
        self.max_retries = max_retries
        self.retry_delay = retry_delay

    # ... (previous methods remain the same)

    async def get_response_with_retry(self, prompt, model="gpt-3.5-turbo", max_tokens=150):
        for attempt in range(self.max_retries):
            try:
                return await self.get_response(prompt, model, max_tokens)
            except AIClientError as e:
                if attempt == self.max_retries - 1:
                    raise
                print_colored(f"Error occurred: {str(e)}. Retrying in {self.retry_delay} seconds...", "yellow")
                await asyncio.sleep(self.retry_delay)

    async def get_streaming_response_with_retry(self, prompt, model="gpt-3.5-turbo", max_tokens=150):
        for attempt in range(self.max_retries):
            try:
                async for chunk in self.get_streaming_response(prompt, model, max_tokens):
                    yield chunk
                return
            except AIClientError as e:
                if attempt == self.max_retries - 1:
                    raise
                print_colored(f"Error occurred: {str(e)}. Retrying in {self.retry_delay} seconds...", "yellow")
                await asyncio.sleep(self.retry_delay)

class AIClientError(Exception):
    pass
```

Now update the `AskCommand` and `ChatCommand` to use these new retry methods:

```python
# ai_cli_tool/commands/ask.py

# ... (previous imports remain the same)

class AskCommand(BaseCommand):
    # ... (previous methods remain the same)

    async def execute_async(self, args):
        prompt = " ".join(args[1:])
        if not prompt:
            print_colored("Please provide a question to ask the AI.", "yellow")
            return

        print_colored("Thinking...", "cyan")
        try:
            async with AIClient() as client:
                response = await client.get_response_with_retry(prompt)
            print_colored("AI response:", "green")
            print(response)
        except AIClientError as e:
            print_colored(str(e), "red")

# ai_cli_tool/commands/chat.py

# ... (previous imports remain the same)

class ChatCommand(BaseCommand):
    # ... (previous methods remain the same)

    async def execute_async(self, args):
        print_colored("Starting chat session. Type 'exit' to end the chat.", "cyan")
        async with AIClient() as client:
            while True:
                user_input = input("You: ")
                if user_input.lower() == 'exit':
                    break

                print_colored("AI: ", "green", end="")
                try:
                    async for chunk in client.get_streaming_response_with_retry(user_input):
                        print(chunk, end="", flush=True)
                    print()  # New line after response
                except AIClientError as e:
                    print_colored(str(e), "red")

        print_colored("Chat session ended.", "cyan")
```

<a name="conclusion"></a>
## 9. Conclusion

In this lesson, we've successfully integrated AI capabilities into our CLI tool. We've implemented:

1. An AI client for communicating with the OpenAI API
2. Basic AI responses using the `ask` command
3. Streaming responses for an interactive chat experience
4. A code generation command as an example of more advanced AI-powered features
5. Error handling and retry mechanisms for improved reliability

These features provide a solid foundation for an AI-assisted developer tool. In the next lesson, we'll focus on enhancing our file handling capabilities and integrating them with our AI features to create a more powerful development assistant.

To test your implementation, you can run your CLI tool using:

```
python -m ai_cli_tool.main
```

This will start your AI-assisted Developer CLI Tool with the new AI capabilities implemented in this lesson. You can now use commands like `ask`, `chat`, and `generate_code` to interact with the AI assistant.
