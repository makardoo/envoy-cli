"""Register region CLI group with the main CLI."""
from envoy_cli.cli_region import region_group


def register(cli):
    cli.add_command(region_group)
