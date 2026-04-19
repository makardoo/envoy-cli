"""CLI commands for pipeline management."""
import click
from envoy_cli.pipeline import (
    create_pipeline, get_pipeline, delete_pipeline,
    list_pipelines, update_pipeline, PipelineError,
)

_BASE = click.get_app_dir("envoy-cli")


@click.group("pipeline")
def pipeline_group():
    """Manage env operation pipelines."""


@pipeline_group.command("create")
@click.argument("name")
@click.argument("steps", nargs=-1, required=True)
@click.option("--base-dir", default=_BASE, hidden=True)
def create_cmd(name, steps, base_dir):
    """Create a new pipeline with ordered STEPS."""
    try:
        create_pipeline(base_dir, name, list(steps))
        click.echo(f"Pipeline '{name}' created with {len(steps)} step(s).")
    except PipelineError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@pipeline_group.command("show")
@click.argument("name")
@click.option("--base-dir", default=_BASE, hidden=True)
def show_cmd(name, base_dir):
    """Show steps of a pipeline."""
    try:
        steps = get_pipeline(base_dir, name)
        for i, step in enumerate(steps, 1):
            click.echo(f"  {i}. {step}")
    except PipelineError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@pipeline_group.command("update")
@click.argument("name")
@click.argument("steps", nargs=-1, required=True)
@click.option("--base-dir", default=_BASE, hidden=True)
def update_cmd(name, steps, base_dir):
    """Replace steps of an existing pipeline."""
    try:
        update_pipeline(base_dir, name, list(steps))
        click.echo(f"Pipeline '{name}' updated.")
    except PipelineError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@pipeline_group.command("delete")
@click.argument("name")
@click.option("--base-dir", default=_BASE, hidden=True)
def delete_cmd(name, base_dir):
    """Delete a pipeline."""
    try:
        delete_pipeline(base_dir, name)
        click.echo(f"Pipeline '{name}' deleted.")
    except PipelineError as e:
        click.echo(f"Error: {e}", err=True)
        raise SystemExit(1)


@pipeline_group.command("list")
@click.option("--base-dir", default=_BASE, hidden=True)
def list_cmd(base_dir):
    """List all pipelines."""
    names = list_pipelines(base_dir)
    if not names:
        click.echo("No pipelines defined.")
    for n in names:
        click.echo(n)
