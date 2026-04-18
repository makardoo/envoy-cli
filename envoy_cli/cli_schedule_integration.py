"""Register schedule commands into the main CLI group.

Import and call `register(cli)` from envoy_cli/cli.py to attach
the schedule sub-group.
"""
from envoy_cli.cli_schedule import schedule_group


def register(cli_group) -> None:
    """Attach the schedule command group to the root CLI.

    Args:
        cli_group: The root Click group to which the schedule
            sub-group will be added.

    Raises:
        TypeError: If *cli_group* does not support ``add_command``.
    """
    if not hasattr(cli_group, "add_command"):
        raise TypeError(
            f"Expected a Click group with 'add_command', got {type(cli_group).__name__!r}"
        )
    cli_group.add_command(schedule_group)
