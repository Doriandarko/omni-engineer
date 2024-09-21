# backend/cli/main.py

import click
from .commands import ai_commands, file_commands, git_commands, project_commands

@click.group()
def cli():
    """AI-Assisted Developer CLI Tool"""
    pass

# Add command groups
cli.add_command(ai_commands.ai)
cli.add_command(file_commands.file)
cli.add_command(git_commands.git)
cli.add_command(project_commands.project)

if __name__ == '__main__':
    cli()