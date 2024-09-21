# Lesson 6: Advanced CLI Features

## Introduction

In this lesson, we'll implement advanced features to enhance our AI-assisted CLI tool. We'll focus on four main areas:

1. Syntax highlighting for code
2. Diff display for file changes
3. Chat history system
4. Save and load functionality for chat sessions

These features will significantly improve the user experience and functionality of our CLI tool.

## Project Structure

Before we dive into the implementation, let's review our updated project structure:

```
ai_cli_tool/
│
├── main.py
├── cli.py
├── ai_integration.py
├── file_handler.py
├── context_manager.py
├── web_search.py
├── image_handler.py
├── syntax_highlighter.py  # New file for this lesson
├── diff_display.py        # New file for this lesson
├── chat_history.py        # New file for this lesson
├── session_manager.py     # New file for this lesson
├── utils.py
├── .env
├── requirements.txt
└── README.md
```

## 1. Implementing Syntax Highlighting for Code

First, let's create a `SyntaxHighlighter` class in `syntax_highlighter.py` to handle code highlighting:

```python
# syntax_highlighter.py

from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import TerminalFormatter
from pygments.util import ClassNotFound

class SyntaxHighlighter:
    @staticmethod
    def highlight_code(code: str, language: str = None) -> str:
        try:
            if language:
                lexer = get_lexer_by_name(language, stripall=True)
            else:
                lexer = guess_lexer(code)
            
            return highlight(code, lexer, TerminalFormatter())
        except ClassNotFound:
            # If language is not recognized, return the original code
            return code

    @staticmethod
    def highlight_file(file_content: str, file_extension: str) -> str:
        language_map = {
            'py': 'python',
            'js': 'javascript',
            'html': 'html',
            'css': 'css',
            'java': 'java',
            'cpp': 'cpp',
            'c': 'c',
            'go': 'go',
            'rs': 'rust',
            'rb': 'ruby',
            'php': 'php',
            'ts': 'typescript',
            'swift': 'swift',
            'kt': 'kotlin',
            'scala': 'scala',
            'md': 'markdown',
            'json': 'json',
            'yaml': 'yaml',
            'sql': 'sql',
            'sh': 'bash',
        }
        
        language = language_map.get(file_extension.lower())
        return SyntaxHighlighter.highlight_code(file_content, language)
```

This `SyntaxHighlighter` class uses the `pygments` library to provide syntax highlighting for various programming languages. It can guess the language if not specified, and handles file extensions for common languages.

Now, let's update our `cli.py` to use syntax highlighting when displaying file contents:

```python
# cli.py

import click
from syntax_highlighter import SyntaxHighlighter
from file_handler import FileHandler

file_handler = FileHandler()
highlighter = SyntaxHighlighter()

@cli.command()
@click.argument('filepath')
def show_file(filepath: str):
    """Display the contents of a file with syntax highlighting"""
    content = file_handler.read_file(filepath)
    if content:
        file_extension = filepath.split('.')[-1] if '.' in filepath else ''
        highlighted_content = highlighter.highlight_file(content, file_extension)
        click.echo(highlighted_content)
    else:
        click.echo(f"Failed to read file: {filepath}")

# ... (other CLI commands)
```

## 2. Adding Diff Display for File Changes

Next, let's implement a diff display feature in `diff_display.py`:

```python
# diff_display.py

import difflib
from typing import List
from colorama import Fore, Back, Style

class DiffDisplay:
    @staticmethod
    def generate_diff(old_content: str, new_content: str) -> List[str]:
        differ = difflib.Differ()
        diff = list(differ.compare(old_content.splitlines(), new_content.splitlines()))
        return diff

    @staticmethod
    def colorize_diff(diff: List[str]) -> str:
        colorized = []
        for line in diff:
            if line.startswith('+'):
                colorized.append(f"{Fore.GREEN}{line}{Style.RESET_ALL}")
            elif line.startswith('-'):
                colorized.append(f"{Fore.RED}{line}{Style.RESET_ALL}")
            elif line.startswith('?'):
                colorized.append(f"{Fore.YELLOW}{line}{Style.RESET_ALL}")
            else:
                colorized.append(line)
        return '\n'.join(colorized)

    @staticmethod
    def display_diff(old_content: str, new_content: str):
        diff = DiffDisplay.generate_diff(old_content, new_content)
        colorized_diff = DiffDisplay.colorize_diff(diff)
        print(colorized_diff)
```

This `DiffDisplay` class uses the `difflib` module to generate diffs between two versions of a file, and `colorama` to colorize the output for better readability.

Let's update our `cli.py` to include a diff command:

```python
# cli.py

from diff_display import DiffDisplay

diff_display = DiffDisplay()

@cli.command()
@click.argument('filepath')
@click.option('--old-version', help='Path to the old version of the file')
def show_diff(filepath: str, old_version: str = None):
    """Display the diff between the current file and its previous version"""
    current_content = file_handler.read_file(filepath)
    if current_content is None:
        return
    
    if old_version:
        old_content = file_handler.read_file(old_version)
        if old_content is None:
            return
    else:
        old_content = context_manager.get_file_version(filepath, -1)  # Get the previous version
    
    if old_content:
        diff_display.display_diff(old_content, current_content)
    else:
        click.echo("No previous version found for comparison")

# ... (other CLI commands)
```

## 3. Implementing a Chat History System

Now, let's create a `ChatHistory` class in `chat_history.py` to manage our chat history:

```python
# chat_history.py

from typing import List, Dict
from collections import deque

class ChatHistory:
    def __init__(self, max_length: int = 100):
        self.history: deque = deque(maxlen=max_length)

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})

    def get_history(self) -> List[Dict[str, str]]:
        return list(self.history)

    def clear_history(self):
        self.history.clear()

    def get_last_n_messages(self, n: int) -> List[Dict[str, str]]:
        return list(self.history)[-n:]

    def remove_last_message(self):
        if self.history:
            self.history.pop()
```

This `ChatHistory` class uses a `deque` (double-ended queue) to efficiently manage chat history with a maximum length.

Let's update our `ai_integration.py` to use the chat history:

```python
# ai_integration.py

from chat_history import ChatHistory

class AIAssistant:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        # ... (previous initialization code)
        self.chat_history = ChatHistory()

    def generate_response(self, prompt: str) -> str:
        context = self.context_manager.get_context()
        
        # Add system message and context
        messages = [
            {"role": "system", "content": "You are an AI assistant for developers. Use the following context to assist with coding tasks and questions."},
            {"role": "user", "content": context},
        ]
        
        # Add recent chat history
        messages.extend(self.chat_history.get_last_n_messages(5))
        
        # Add current prompt
        messages.append({"role": "user", "content": prompt})

        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages
            )
            ai_response = response.choices[0].message['content']
            
            # Add the interaction to chat history
            self.chat_history.add_message("user", prompt)
            self.chat_history.add_message("assistant", ai_response)
            
            return ai_response
        except Exception as e:
            return f"Error generating AI response: {e}"

    # ... (other methods)
```

## 4. Implementing Save and Load Functionality for Chat Sessions

Finally, let's create a `SessionManager` class in `session_manager.py` to handle saving and loading chat sessions:

```python
# session_manager.py

import json
from typing import Dict, Any
from chat_history import ChatHistory
from context_manager import ContextManager

class SessionManager:
    @staticmethod
    def save_session(filename: str, chat_history: ChatHistory, context_manager: ContextManager):
        session_data = {
            "chat_history": chat_history.get_history(),
            "files": context_manager.files,
            "search_results": context_manager.search_results,
            "images": context_manager.images
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(session_data, f)
            return True
        except IOError as e:
            print(f"Error saving session: {e}")
            return False

    @staticmethod
    def load_session(filename: str) -> Dict[str, Any]:
        try:
            with open(filename, 'r') as f:
                session_data = json.load(f)
            return session_data
        except IOError as e:
            print(f"Error loading session: {e}")
            return {}

    @staticmethod
    def restore_session(chat_history: ChatHistory, context_manager: ContextManager, session_data: Dict[str, Any]):
        if "chat_history" in session_data:
            chat_history.clear_history()
            for message in session_data["chat_history"]:
                chat_history.add_message(message["role"], message["content"])
        
        if "files" in session_data:
            context_manager.files = session_data["files"]
        
        if "search_results" in session_data:
            context_manager.search_results = session_data["search_results"]
        
        if "images" in session_data:
            context_manager.images = session_data["images"]
```

Now, let's update our `cli.py` to include save and load commands:

```python
# cli.py

from session_manager import SessionManager

session_manager = SessionManager()

@cli.command()
@click.argument('filename')
def save_session(filename: str):
    """Save the current chat session to a file"""
    if session_manager.save_session(filename, ai_assistant.chat_history, context_manager):
        click.echo(f"Session saved to {filename}")
    else:
        click.echo("Failed to save session")

@cli.command()
@click.argument('filename')
def load_session(filename: str):
    """Load a chat session from a file"""
    session_data = session_manager.load_session(filename)
    if session_data:
        session_manager.restore_session(ai_assistant.chat_history, context_manager, session_data)
        click.echo(f"Session loaded from {filename}")
    else:
        click.echo("Failed to load session")

# ... (other CLI commands)
```

## Conclusion

In this lesson, we've implemented several advanced CLI features to enhance our AI-assisted developer tool:

1. Syntax highlighting for code, improving readability when displaying file contents.
2. Diff display for file changes, allowing users to easily see modifications.
3. A chat history system, providing context for the AI assistant and enabling more coherent conversations.
4. Save and load functionality for chat sessions, allowing users to persist their work across multiple sessions.

These features significantly improve the user experience and functionality of our CLI tool, making it more powerful and flexible for developers.

## Exercises

1. Implement a command to display the chat history with syntax highlighting for code snippets within the conversation.
2. Add a feature to export the chat history as a formatted Markdown file, including syntax-highlighted code blocks.
3. Implement a "time travel" feature that allows users to revert the entire session (including file contents and context) to a previous state.
4. Create a command to compare two saved sessions and display the differences in context and chat history.

By completing these exercises, you'll gain a deeper understanding of managing complex CLI features and working with persistent data in an AI-assisted development environment.
