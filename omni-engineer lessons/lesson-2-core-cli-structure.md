# Lesson 2: Building the Core CLI Structure and Basic Commands

## Table of Contents
1. [Introduction](#introduction)
2. [Project Structure](#project-structure)
3. [Creating a Command Parser](#command-parser)
4. [Implementing Basic Commands](#basic-commands)
5. [Adding Colorful Output](#colorful-output)
6. [Handling User Input](#user-input)
7. [Advanced CLI Features](#advanced-features)
8. [Conclusion](#conclusion)

<a name="introduction"></a>
## 1. Introduction

In this lesson, we'll focus on building a robust core CLI structure for our AI-assisted developer tool. We'll implement a command parser, add basic commands, incorporate colorful output, and handle user input effectively. By the end of this lesson, you'll have a solid foundation for your CLI tool that you can easily extend with AI capabilities in future lessons.

<a name="project-structure"></a>
## 2. Project Structure

Let's start by updating our project structure to accommodate the new features we'll be implementing:

```
ai_cli_tool/
│
├── ai_cli_tool/
│   ├── __init__.py
│   ├── main.py
│   ├── cli.py            # New file for CLI logic
│   ├── commands/         # New directory for command implementations
│   │   ├── __init__.py
│   │   ├── base.py       # Base command class
│   │   ├── help.py       # Help command
│   │   └── exit.py       # Exit command
│   ├── ai_integration.py
│   ├── file_handler.py
│   ├── utils.py
│   └── config.py
│
├── tests/
│   ├── __init__.py
│   ├── test_cli.py       # New test file for CLI functionality
│   ├── test_commands.py  # New test file for commands
│   ├── test_ai_integration.py
│   ├── test_file_handler.py
│   └── test_utils.py
│
├── .env
├── requirements.txt
├── setup.py
└── README.md
```

<a name="command-parser"></a>
## 3. Creating a Command Parser

We'll use the `cmd` module from the Python standard library to create our command parser. This module provides a simple framework for building line-oriented command interpreters.

Let's create the `cli.py` file:

```python
# ai_cli_tool/cli.py

import cmd
import sys
from .utils import print_colored
from .commands import get_command

class AICLI(cmd.Cmd):
    intro = "Welcome to the AI-assisted Developer CLI Tool. Type 'help' or '?' to list commands."
    prompt = "(ai-cli) "

    def default(self, line):
        command = get_command(line)
        if command:
            command.execute(line)
        else:
            print_colored(f"Unknown command: {line}", "red")

    def do_exit(self, arg):
        """Exit the CLI tool"""
        print_colored("Thank you for using the AI-assisted Developer CLI Tool. Goodbye!", "yellow")
        return True

    def emptyline(self):
        """Do nothing on empty input line"""
        pass

def main():
    AICLI().cmdloop()

if __name__ == "__main__":
    main()
```

This `AICLI` class inherits from `cmd.Cmd` and provides the core structure for our CLI. The `default` method handles commands that aren't explicitly defined, allowing us to implement a more flexible command system.

<a name="basic-commands"></a>
## 4. Implementing Basic Commands

Now, let's implement the base command structure and two basic commands: help and exit.

First, create the base command class in `ai_cli_tool/commands/base.py`:

```python
# ai_cli_tool/commands/base.py

from abc import ABC, abstractmethod

class BaseCommand(ABC):
    @abstractmethod
    def execute(self, args):
        pass

    @classmethod
    @abstractmethod
    def name(cls):
        pass

    @classmethod
    @abstractmethod
    def description(cls):
        pass
```

Now, let's implement the help command in `ai_cli_tool/commands/help.py`:

```python
# ai_cli_tool/commands/help.py

from .base import BaseCommand
from ..utils import print_colored

class HelpCommand(BaseCommand):
    @classmethod
    def name(cls):
        return "help"

    @classmethod
    def description(cls):
        return "Display help information for available commands"

    def execute(self, args):
        print_colored("Available commands:", "cyan")
        for command in BaseCommand.__subclasses__():
            print_colored(f"  {command.name()}: {command.description()}", "cyan")
```

Next, implement the exit command in `ai_cli_tool/commands/exit.py`:

```python
# ai_cli_tool/commands/exit.py

from .base import BaseCommand
from ..utils import print_colored

class ExitCommand(BaseCommand):
    @classmethod
    def name(cls):
        return "exit"

    @classmethod
    def description(cls):
        return "Exit the CLI tool"

    def execute(self, args):
        print_colored("Thank you for using the AI-assisted Developer CLI Tool. Goodbye!", "yellow")
        raise SystemExit
```

Finally, update the `ai_cli_tool/commands/__init__.py` file to include a function for getting the appropriate command:

```python
# ai_cli_tool/commands/__init__.py

from .help import HelpCommand
from .exit import ExitCommand

def get_command(command_name):
    commands = {
        HelpCommand.name(): HelpCommand,
        ExitCommand.name(): ExitCommand,
    }
    return commands.get(command_name.split()[0].lower())()
```

<a name="colorful-output"></a>
## 5. Adding Colorful Output

We've already used the `print_colored` function from our `utils.py` file. Let's enhance it to support more colors and styles:

```python
# ai_cli_tool/utils.py

from colorama import init, Fore, Back, Style

init(autoreset=True)

def print_colored(text, color="white", bg_color=None, style=None):
    color_map = {
        "black": Fore.BLACK,
        "red": Fore.RED,
        "green": Fore.GREEN,
        "yellow": Fore.YELLOW,
        "blue": Fore.BLUE,
        "magenta": Fore.MAGENTA,
        "cyan": Fore.CYAN,
        "white": Fore.WHITE,
    }
    bg_color_map = {
        "black": Back.BLACK,
        "red": Back.RED,
        "green": Back.GREEN,
        "yellow": Back.YELLOW,
        "blue": Back.BLUE,
        "magenta": Back.MAGENTA,
        "cyan": Back.CYAN,
        "white": Back.WHITE,
    }
    style_map = {
        "dim": Style.DIM,
        "normal": Style.NORMAL,
        "bright": Style.BRIGHT,
    }

    output = ""
    if style:
        output += style_map.get(style.lower(), "")
    output += color_map.get(color.lower(), "")
    if bg_color:
        output += bg_color_map.get(bg_color.lower(), "")
    output += text
    print(output)
```

<a name="user-input"></a>
## 6. Handling User Input

To improve user input handling, we'll use the `prompt_toolkit` library. First, update your `requirements.txt` file:

```
click==8.1.3
openai==0.27.0
python-dotenv==0.19.2
colorama==0.4.4
prompt_toolkit==3.0.28
```

Now, let's update our `cli.py` file to use `prompt_toolkit`:

```python
# ai_cli_tool/cli.py

import cmd
import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from .utils import print_colored
from .commands import get_command

class AICLI(cmd.Cmd):
    intro = "Welcome to the AI-assisted Developer CLI Tool. Type 'help' or '?' to list commands."
    prompt = "(ai-cli) "

    def __init__(self):
        super().__init__()
        self.session = PromptSession(
            history=FileHistory('.ai_cli_history'),
            auto_suggest=AutoSuggestFromHistory(),
        )

    def cmdloop(self, intro=None):
        self.preloop()
        if intro is not None:
            self.intro = intro
        if self.intro:
            print_colored(self.intro, "cyan")
        stop = None
        while not stop:
            try:
                line = self.session.prompt(self.prompt)
                line = self.precmd(line)
                stop = self.onecmd(line)
                stop = self.postcmd(stop, line)
            except KeyboardInterrupt:
                print_colored("^C", "red")
            except EOFError:
                print_colored("^D", "red")
                break
        self.postloop()

    def default(self, line):
        command = get_command(line)
        if command:
            command.execute(line)
        else:
            print_colored(f"Unknown command: {line}", "red")

    def emptyline(self):
        """Do nothing on empty input line"""
        pass

def main():
    AICLI().cmdloop()

if __name__ == "__main__":
    main()
```

This implementation uses `PromptSession` from `prompt_toolkit` to provide features like command history and auto-suggestions.

<a name="advanced-features"></a>
## 7. Advanced CLI Features

To further enhance our CLI, let's add command completion. Update the `cli.py` file:

```python
# ai_cli_tool/cli.py

import cmd
import sys
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from .utils import print_colored
from .commands import get_command, get_all_commands

class AICLI(cmd.Cmd):
    intro = "Welcome to the AI-assisted Developer CLI Tool. Type 'help' or '?' to list commands."
    prompt = "(ai-cli) "

    def __init__(self):
        super().__init__()
        self.commands = get_all_commands()
        self.completer = WordCompleter([cmd.name() for cmd in self.commands])
        self.session = PromptSession(
            history=FileHistory('.ai_cli_history'),
            auto_suggest=AutoSuggestFromHistory(),
            completer=self.completer,
        )

    # ... (rest of the code remains the same)

# ... (rest of the file remains the same)
```

Update the `ai_cli_tool/commands/__init__.py` file to include the `get_all_commands` function:

```python
# ai_cli_tool/commands/__init__.py

from .help import HelpCommand
from .exit import ExitCommand

def get_command(command_name):
    commands = {cmd.name(): cmd for cmd in get_all_commands()}
    return commands.get(command_name.split()[0].lower())()

def get_all_commands():
    return [HelpCommand, ExitCommand]
```

<a name="conclusion"></a>
## 8. Conclusion

In this lesson, we've built a robust core CLI structure with basic commands, colorful output, and advanced user input handling. Our CLI now supports:

1. A flexible command system using the `cmd` module
2. Basic 'help' and 'exit' commands
3. Colorful output using `colorama`
4. Enhanced user input handling with command history and auto-suggestions using `prompt_toolkit`
5. Command completion

This foundation provides a solid base for adding AI-assisted features in future lessons. In the next lesson, we'll focus on integrating AI capabilities into our CLI tool.

To test your implementation, update the `main.py` file:

```python
# ai_cli_tool/main.py

from .cli import main

if __name__ == "__main__":
    main()
```

You can now run your CLI tool using:

```
python -m ai_cli_tool.main
```

This will start your AI-assisted Developer CLI Tool with the core structure and basic commands implemented in this lesson.
