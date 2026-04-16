"""CLI commands for merging env files."""
import click
from envoy_cli.merge import merge_envs, MergeStrategy, MergeError
from envoy_cli.env_file import serialize_env, encrypt_env
from envoy_cli.storage import save_env


@click.group(name="merge")
def merge_group():
    """Merge two env environments."""


@merge_group.command(name="run")
@click.argument("base")
@click.argument("other")
@click.option("--passphrase", prompt=True, hide_input=True)
@click.option(
    "--strategy",
    type=click.Choice([s.value for s in MergeStrategy]),
    default=MergeStrategy.OURS.value,
    show_default=True,
    help="Conflict resolution strategy.",
)
@click.option("--output", default=None, help="Save merged result as this env name.")
@click.option("--show-conflicts", is_flag=True, default=False)
def run_merge(base, other, passphrase, strategy, output, show_conflicts):
    """Merge OTHER into BASE env."""
    try:
        result = merge_envs(base, other, passphrase, MergeStrategy(strategy))
    except MergeError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)

    if result.conflicts:
        click.echo(f"⚠  {len(result.conflicts)} conflict(s) resolved via '{strategy}':")
        if show_conflicts:
            for c in result.conflicts:
                click.echo(f"  {c.key}: base={c.base_value!r} other={c.other_value!r}")
    else:
        click.echo("✓ No conflicts.")

    if output:
        plain = serialize_env(list(result.merged.items()))
        encrypted = encrypt_env(plain, passphrase)
        save_env(output, encrypted)
        click.echo(f"Merged env saved as '{output}'.")
    else:
        for key, val in result.merged.items():
            click.echo(f"{key}={val}")
