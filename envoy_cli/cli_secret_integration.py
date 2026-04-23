"""Register the secret group with the main CLI."""

from envoy_cli.cli_secret import secret_group


def register(cli):
    cli.add_command(secret_group)
