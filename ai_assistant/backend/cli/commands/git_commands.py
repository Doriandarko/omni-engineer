# backend/cli/commands/git_commands.py

import click
from ...core.git_integration import GitIntegration

git_integration = GitIntegration()

@click.group()
def git():
    """Git-related commands"""
    pass

@git.command()
@click.option('--message', '-m', help='Commit message')
def commit(message):
    """Commit changes to the repository"""
    result = git_integration.commit(message)
    click.echo(result)

@git.command()
@click.argument('branch_name')
def create_branch(branch_name):
    """Create a new branch"""
    result = git_integration.create_branch(branch_name)
    click.echo(result)

@git.command()
def current_branch():
    """Show the current branch"""
    branch = git_integration.get_current_branch()
    click.echo(f"Current branch: {branch}")

@git.command()
def list_branches():
    """List all branches"""
    branches = git_integration.list_branches()
    click.echo("Branches:")
    for branch in branches:
        click.echo(f"- {branch}")

@git.command()
def review():
    """Perform an AI-assisted code review"""
    review = git_integration.perform_code_review()
    click.echo("AI Code Review:")
    click.echo(review)