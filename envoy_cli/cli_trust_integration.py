"""Register trust CLI group with the main CLI."""
from .cli_trust import trust_group


def register(cli) -> None:  # type: ignore[type-arg]
    cli.add_command(trust_group)
