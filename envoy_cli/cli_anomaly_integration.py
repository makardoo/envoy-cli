"""Register anomaly CLI group with the main cli."""
from envoy_cli.cli_anomaly import anomaly_group


def register(cli) -> None:  # type: ignore[type-arg]
    cli.add_command(anomaly_group)
