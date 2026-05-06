"""Register the risk CLI group with the main cli."""

from envoy_cli.cli_risk import risk_group


def register(cli):
    cli.add_command(risk_group)
