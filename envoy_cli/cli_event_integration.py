"""Register event CLI group with the main CLI."""
from envoy_cli.cli_event import event_group


def register(cli):
    cli.add_command(event_group)
