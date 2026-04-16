"""CLI commands for searching env files."""
import click
from envoy_cli.search import search_key, search_value
from envoy_cli.storage import get_env_dir


@click.group(name="search")
def search_group():
    """Search across env files."""


@search_group.command("key")
@click.argument("pattern")
@click.option("--passphrase", envvar="ENVOY_PASSPHRASE", prompt=True, hide_input=True)
@click.option("--env", default=None, help="Limit search to a specific env.")
@click.option("--base-dir", default=None, hidden=True)
def search_key_cmd(pattern, passphrase, env, base_dir):
    """Search for keys matching PATTERN."""
    base = base_dir or get_env_dir()
    results = search_key(base, passphrase, pattern, env)
    if not results:
        click.echo("No matches found.")
        return
    for env_name, k, v in results:
        click.echo(f"[{env_name}] {k}={v}")


@search_group.command("value")
@click.argument("pattern")
@click.option("--passphrase", envvar="ENVOY_PASSPHRASE", prompt=True, hide_input=True)
@click.option("--env", default=None, help="Limit search to a specific env.")
@click.option("--base-dir", default=None, hidden=True)
def search_value_cmd(pattern, passphrase, env, base_dir):
    """Search for values matching PATTERN."""
    base = base_dir or get_env_dir()
    results = search_value(base, passphrase, pattern, env)
    if not results:
        click.echo("No matches found.")
        return
    for env_name, k, _ in results:
        click.echo(f"[{env_name}] {k}=***")
