"""CLI commands for the affinity feature."""
from __future__ import annotations

import click

from envoy_cli.affinity import (
    AffinityError,
    set_affinity,
    get_affinity,
    remove_affinity,
    list_affinities,
    list_all,
)

_STRENGTHS = ["weak", "moderate", "strong"]
_DEFAULT_BASE = click.get_app_dir("envoy")


@click.group("affinity")
def affinity_group() -> None:
    """Manage environment affinities."""


@affinity_group.command("set")
@click.argument("env_name")
@click.argument("related")
@click.option("--strength", default="weak", type=click.Choice(_STRENGTHS), show_default=True)
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def set_cmd(env_name: str, related: str, strength: str, base_dir: str) -> None:
    """Set affinity between ENV_NAME and RELATED."""
    try:
        set_affinity(base_dir, env_name, related, strength)
        click.echo(f"Affinity set: {env_name} <-> {related} ({strength})")
    except AffinityError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@affinity_group.command("get")
@click.argument("env_name")
@click.argument("related")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def get_cmd(env_name: str, related: str, base_dir: str) -> None:
    """Get affinity strength between ENV_NAME and RELATED."""
    try:
        strength = get_affinity(base_dir, env_name, related)
        click.echo(strength)
    except AffinityError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@affinity_group.command("remove")
@click.argument("env_name")
@click.argument("related")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def remove_cmd(env_name: str, related: str, base_dir: str) -> None:
    """Remove affinity between ENV_NAME and RELATED."""
    try:
        remove_affinity(base_dir, env_name, related)
        click.echo(f"Affinity removed: {env_name} <-> {related}")
    except AffinityError as exc:
        click.echo(f"Error: {exc}", err=True)
        raise SystemExit(1)


@affinity_group.command("list")
@click.argument("env_name")
@click.option("--base-dir", default=_DEFAULT_BASE, hidden=True)
def list_cmd(env_name: str, base_dir: str) -> None:
    """List all affinities for ENV_NAME."""
    affinities = list_affinities(base_dir, env_name)
    if not affinities:
        click.echo(f"No affinities recorded for {env_name!r}.")
        return
    for related, strength in sorted(affinities.items()):
        click.echo(f"  {related}: {strength}")
