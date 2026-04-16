"""Register pin commands with the main CLI."""
from envoy_cli.cli_pin import pin_group


def register(cli):
    """Attach the pin command group to the root CLI."""
    cli.add_command(pin_group)
