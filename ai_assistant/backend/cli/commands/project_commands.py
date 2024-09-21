# backend/cli/commands/project_commands.py

import click
from ...core.code_analyzer import CodeAnalyzer
from ...core.vector_db import VectorDB

code_analyzer = CodeAnalyzer()
vector_db = VectorDB()

@click.group()
def project():
    """Project-related commands"""
    pass

@project.command()
@click.argument('project_path')
def analyze(project_path):
    """Analyze a project"""
    analysis = code_analyzer.analyze_project(project_path)
    click.echo("Project Analysis:")
    for file, file_analysis in analysis.items():
        click.echo(f"\nFile: {file}")
        for item in file_analysis:
            click.echo(f"- {item['type']}: {item['message']} (line {item['line']})")

@project.command()
@click.argument('project_path')
def add_to_context(project_path):
    """Add a project to the AI context"""
    project_files = code_analyzer.get_project_files(project_path)
    for file_path, content in project_files.items():
        vector_db.add_document(file_path, content)
    click.echo(f"Added {len(project_files)} files to the context")

@project.command()
def summary():
    """Get a summary of the current project"""
    # This would typically involve querying the vector database or other storage
    # for project-related information
    click.echo("Project summary not implemented")