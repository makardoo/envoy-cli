"""Register workflow_group into the main CLI."""
from envoy_cli.cli_workflow import workflow_group


def register(cli):
    cli.add_command(workflow_group)
