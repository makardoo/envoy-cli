"""Register confidence commands with the main CLI."""
from envoy_cli.cli_confidence import confidence_group


def register(cli):
    cli.add_command(confidence_group)
