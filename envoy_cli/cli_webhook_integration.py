"""Register webhook CLI group into the main CLI."""
from envoy_cli.cli_webhook import webhook_group


def register(cli):
    """Attach the webhook command group to *cli*."""
    cli.add_command(webhook_group)
