"""Register cadence commands with the main CLI."""
from envoy_cli.cli_cadence import cadence_group


def register(cli):
    cli.add_command(cadence_group)
