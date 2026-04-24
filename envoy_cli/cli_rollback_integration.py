"""Register rollback CLI group with the main CLI."""
from envoy_cli.cli_rollback import rollback_group


def register(cli) -> None:  # noqa: ANN001
    cli.add_command(rollback_group)
