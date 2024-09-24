# Lesson 4: File Handling and Context Management

## Introduction

In this lesson, we'll focus on implementing file handling capabilities and context management for our AI-assisted CLI tool. These features are crucial for developers working on projects with multiple files and for maintaining the AI's understanding of the codebase.

## Project Structure

Before we dive into the implementation, let's review our project structure:

```
ai_cli_tool/
│
├── main.py
├── cli.py
├── ai_integration.py
├── file_handler.py  # New file for this lesson
├── context_manager.py  # New file for this lesson
├── utils.py
├── .env
├── requirements.txt
└── README.md
```

## 1. Implementing File Reading and Writing

Let's start by creating a `FileHandler` class in `file_handler.py` to manage file operations.

```python
# file_handler.py

import os
from typing import Optional

class FileHandler:
    def __init__(self, base_path: str = "."):
        self.base_path = base_path

    def read_file(self, filepath: str) -> Optional[str]:
        full_path = os.path.join(self.base_path, filepath)
        try:
            with open(full_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            print(f"Error: File not found: {filepath}")
            return None
        except IOError as e:
            print(f"Error reading {filepath}: {e}")
            return None

    def write_file(self, filepath: str, content: str) -> bool:
        full_path = os.path.join(self.base_path, filepath)
        try:
            with open(full_path, 'w', encoding='utf-8') as file:
                file.write(content)
            return True
        except IOError as e:
            print(f"Error writing to {filepath}: {e}")
            return False

    def file_exists(self, filepath: str) -> bool:
        full_path = os.path.join(self.base_path, filepath)
        return os.path.isfile(full_path)
```

This `FileHandler` class provides methods for reading, writing, and checking the existence of files. It uses a `base_path` to allow for relative file paths.

## 2. Adding and Editing Files

Now, let's update our CLI to include commands for adding and editing files. We'll modify `cli.py`:

```python
# cli.py

import click
from file_handler import FileHandler
from context_manager import ContextManager

file_handler = FileHandler()
context_manager = ContextManager()

@click.group()
def cli():
    """AI-Assisted Developer CLI Tool"""
    pass

@cli.command()
@click.argument('filepath')
def add_file(filepath):
    """Add a file to the AI context"""
    content = file_handler.read_file(filepath)
    if content is not None:
        context_manager.add_file(filepath, content)
        click.echo(f"Added file: {filepath}")
    else:
        click.echo(f"Failed to add file: {filepath}")

@cli.command()
@click.argument('filepath')
def edit_file(filepath):
    """Edit a file in the AI context"""
    if not file_handler.file_exists(filepath):
        click.echo(f"File not found: {filepath}")
        return

    content = file_handler.read_file(filepath)
    if content is None:
        return

    click.echo(f"Current content of {filepath}:")
    click.echo(content)
    
    new_content = click.edit(content)
    if new_content is not None:
        if file_handler.write_file(filepath, new_content):
            context_manager.update_file(filepath, new_content)
            click.echo(f"File updated: {filepath}")
        else:
            click.echo(f"Failed to update file: {filepath}")
    else:
        click.echo("No changes made.")

if __name__ == '__main__':
    cli()
```

## 3. Managing AI Context with File Content

To manage the AI context, we'll create a `ContextManager` class in `context_manager.py`:

```python
# context_manager.py

from typing import Dict, List

class ContextManager:
    def __init__(self):
        self.files: Dict[str, str] = {}
        self.history: List[Dict[str, str]] = []

    def add_file(self, filepath: str, content: str):
        self.files[filepath] = content
        self.history.append({"action": "add", "filepath": filepath})

    def update_file(self, filepath: str, content: str):
        if filepath in self.files:
            self.files[filepath] = content
            self.history.append({"action": "update", "filepath": filepath})
        else:
            print(f"File not in context: {filepath}")

    def remove_file(self, filepath: str):
        if filepath in self.files:
            del self.files[filepath]
            self.history.append({"action": "remove", "filepath": filepath})
        else:
            print(f"File not in context: {filepath}")

    def get_context(self) -> str:
        context = "Current files in context:\n\n"
        for filepath, content in self.files.items():
            context += f"File: {filepath}\n```\n{content}\n```\n\n"
        return context

    def get_history(self) -> str:
        return "\n".join([f"{action['action'].capitalize()}: {action['filepath']}" for action in self.history])
```

This `ContextManager` class keeps track of the files added to the AI context and maintains a history of actions performed on these files.

## 4. Implementing Undo Functionality

To implement undo functionality, we'll add an `UndoManager` class in `utils.py`:

```python
# utils.py

from typing import Dict, List, Callable

class UndoManager:
    def __init__(self):
        self.history: List[Dict[str, Callable]] = []

    def add_action(self, undo_func: Callable, redo_func: Callable):
        self.history.append({"undo": undo_func, "redo": redo_func})

    def undo(self):
        if self.history:
            action = self.history.pop()
            action["undo"]()

    def redo(self):
        if self.history:
            action = self.history[-1]
            action["redo"]()
```

Now, let's update our `cli.py` to include undo functionality:

```python
# cli.py

# ... (previous imports)
from utils import UndoManager

# ... (previous code)

undo_manager = UndoManager()

@cli.command()
def undo():
    """Undo the last file operation"""
    undo_manager.undo()
    click.echo("Undo performed")

@cli.command()
def redo():
    """Redo the last undone file operation"""
    undo_manager.redo()
    click.echo("Redo performed")

# Update the add_file function
@cli.command()
@click.argument('filepath')
def add_file(filepath):
    """Add a file to the AI context"""
    content = file_handler.read_file(filepath)
    if content is not None:
        context_manager.add_file(filepath, content)
        undo_manager.add_action(
            lambda: context_manager.remove_file(filepath),
            lambda: context_manager.add_file(filepath, content)
        )
        click.echo(f"Added file: {filepath}")
    else:
        click.echo(f"Failed to add file: {filepath}")

# Update the edit_file function
@cli.command()
@click.argument('filepath')
def edit_file(filepath):
    """Edit a file in the AI context"""
    if not file_handler.file_exists(filepath):
        click.echo(f"File not found: {filepath}")
        return

    old_content = file_handler.read_file(filepath)
    if old_content is None:
        return

    click.echo(f"Current content of {filepath}:")
    click.echo(old_content)
    
    new_content = click.edit(old_content)
    if new_content is not None and new_content != old_content:
        if file_handler.write_file(filepath, new_content):
            context_manager.update_file(filepath, new_content)
            undo_manager.add_action(
                lambda: context_manager.update_file(filepath, old_content),
                lambda: context_manager.update_file(filepath, new_content)
            )
            click.echo(f"File updated: {filepath}")
        else:
            click.echo(f"Failed to update file: {filepath}")
    else:
        click.echo("No changes made.")

# ... (rest of the code)
```

## Conclusion

In this lesson, we've implemented file handling and context management for our AI-assisted CLI tool. We've created classes for file handling, context management, and undo functionality. These features allow developers to:

1. Add files to the AI context
2. Edit files and update the context
3. Undo and redo file operations
4. Maintain a history of file actions

This implementation provides a solid foundation for managing files and maintaining context in an AI-assisted development environment. In the next lesson, we'll focus on integrating these features with the AI component to provide intelligent assistance based on the file context.

## Exercises

1. Implement a `show_context` command that displays the current files in the AI context.
2. Add a `remove_file` command to remove a file from the AI context.
3. Extend the `undo` and `redo` functionality to work with file content changes, not just add/remove operations.
4. Implement a `diff` feature that shows the differences between the current file content and the last saved version in the context.

By completing these exercises, you'll gain a deeper understanding of file handling and context management in an AI-assisted CLI tool.
