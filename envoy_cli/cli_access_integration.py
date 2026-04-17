"""Register access_group into the main CLI."""
from envoy_cli.cli_access import access_group


def register(cli):
    cli.add_command(access_group)
