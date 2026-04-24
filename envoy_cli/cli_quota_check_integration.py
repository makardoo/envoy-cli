"""Register the quota-check command group with the root CLI."""

from envoy_cli.cli_quota_check import quota_check_group


def register(cli) -> None:  # noqa: ANN001
    """Attach *quota_check_group* to *cli*."""
    cli.add_command(quota_check_group)
