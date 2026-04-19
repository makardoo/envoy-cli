"""CLI commands for managing workflows."""
import os
import click
from envoy_cli.workflow import (
    WorkflowError,
    create_workflow,
    get_workflow,
    update_workflow,
    delete_workflow,
    list_workflows,
)

_BASE = os.environ.get("ENVOY_BASE_DIR", os.path.expanduser("~/.envoy"))


@click.group("workflow")
def workflow_group():
    """Manage named workflow sequences."""


@workflow_group.command("create")
@click.argument("name")
@click.argument("steps", nargs=-1, required=True)
def create_cmd(name, steps):
    """Create a workflow with one or more steps."""
    try:
        entry = create_workflow(_BASE, name, list(steps))
        click.echo(f"Created workflow '{entry['name']}' with {len(entry['steps'])} step(s).")
    except WorkflowError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@workflow_group.command("show")
@click.argument("name")
def show_cmd(name):
    """Show steps in a workflow."""
    try:
        entry = get_workflow(_BASE, name)
        click.echo(f"Workflow: {entry['name']}")
        for i, step in enumerate(entry["steps"], 1):
            click.echo(f"  {i}. {step}")
    except WorkflowError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@workflow_group.command("update")
@click.argument("name")
@click.argument("steps", nargs=-1, required=True)
def update_cmd(name, steps):
    """Replace all steps in a workflow."""
    try:
        entry = update_workflow(_BASE, name, list(steps))
        click.echo(f"Updated workflow '{entry['name']}'.")
    except WorkflowError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@workflow_group.command("delete")
@click.argument("name")
def delete_cmd(name):
    """Delete a workflow."""
    try:
        delete_workflow(_BASE, name)
        click.echo(f"Deleted workflow '{name}'.")
    except WorkflowError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@workflow_group.command("list")
def list_cmd():
    """List all workflows."""
    entries = list_workflows(_BASE)
    if not entries:
        click.echo("No workflows defined.")
        return
    for e in entries:
        click.echo(f"{e['name']} ({len(e['steps'])} step(s))")
