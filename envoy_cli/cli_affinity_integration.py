"""Register the affinity command group with the main CLI."""
from envoy_cli.cli_affinity import affinity_group


def register(cli) -> None:  # noqa: ANN001
    cli.add_command(affinity_group)
