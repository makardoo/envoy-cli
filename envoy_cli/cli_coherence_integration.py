"""Register the coherence command group with the main CLI."""

from envoy_cli.cli_coherence import coherence_group


def register(cli) -> None:  # noqa: ANN001
    cli.add_command(coherence_group)
