"""Register the velocity command group with the root CLI."""
from envoy_cli.cli_velocity import velocity_group


def register(cli: object) -> None:  # type: ignore[type-arg]
    cli.add_command(velocity_group)  # type: ignore[attr-defined]
