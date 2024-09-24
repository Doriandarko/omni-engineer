import pytest
from click.testing import CliRunner
from cli.main import cli

runner = CliRunner()

def test_cli_help():
    result = runner.invoke(cli, ['--help'])
    assert result.exit_code == 0
    assert 'AI-Assisted Developer CLI Tool' in result.output

# Add more CLI tests here