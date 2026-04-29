"""Register spotlight CLI group with the main cli."""

from envoy_cli.cli_spotlight import spotlight_group


def register(cli) -> None:  # type: ignore[type-arg]
    cli.add_command(spotlight_group)
