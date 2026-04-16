"""Register schedule commands into the main CLI group.

Import and call `register(cli)` from envoy_cli/cli.py to attach
the schedule sub-group.
"""
from envoy_cli.cli_schedule import schedule_group


def register(cli_group) -> None:
    """Attach the schedule command group to the root CLI."""
    cli_group.add_command(schedule_group)
