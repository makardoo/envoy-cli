"""Register expiry CLI group with the main cli."""

from envoy_cli.cli_expiry import expiry_group


def register(cli):
    cli.add_command(expiry_group)
