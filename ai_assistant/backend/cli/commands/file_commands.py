# backend/cli/commands/file_commands.py

import click
from ...core.file_handler import FileHandler

file_handler = FileHandler()

@click.group()
def file():
    """File-related commands"""
    pass

@file.command()
@click.argument('filepath')
def add(filepath):
    """Add a file to the AI context"""
    content = file_handler.read_file(filepath)
    if content:
        click.echo(f"Added file: {filepath}")
    else:
        click.echo(f"Failed to add file: {filepath}")

@file.command()
@click.argument('filepath')
def show(filepath):
    """Display the contents of a file"""
    content = file_handler.read_file(filepath)
    if content:
        click.echo(content)
    else:
        click.echo(f"Failed to read file: {filepath}")

@file.command()
@click.argument('filepath')
def delete(filepath):
    """Delete a file"""
    if file_handler.delete_file(filepath):
        click.echo(f"Deleted file: {filepath}")
    else:
        click.echo(f"Failed to delete file: {filepath}")

@file.command()
def list():
    """List all files in the AI context"""
    files = file_handler.list_files()
    for f in files:
        click.echo(f)