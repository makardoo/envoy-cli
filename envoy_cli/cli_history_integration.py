"""Register history commands with the main CLI."""
from envoy_cli.cli_history import history_group


def register(cli):
    cli.add_command(history_group)
