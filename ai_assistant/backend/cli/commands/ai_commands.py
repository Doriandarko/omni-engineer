# backend/cli/commands/ai_commands.py

import click
from ...core.ai_integration import AIIntegration

ai_integration = AIIntegration()

@click.group()
def ai():
    """AI-related commands"""
    pass

@ai.command()
@click.argument('prompt')
def ask(prompt):
    """Ask the AI a question"""
    response = ai_integration.generate_response(prompt)
    click.echo(response)

@ai.command()
@click.argument('prompt')
def stream(prompt):
    """Stream a response from the AI"""
    for chunk in ai_integration.stream_response(prompt):
        click.echo(chunk, nl=False)
    click.echo()

@ai.command()
@click.argument('model')
def switch_model(model):
    """Switch the AI model"""
    new_model = ai_integration.switch_model(model)
    click.echo(f"Switched to model: {new_model}")