"""CLI commands for managing profiles."""

from __future__ import annotations

import json
import sys

import click

from envoy_cli.profile import (
    ProfileError,
    apply_profile,
    delete_profile,
    list_profiles,
    load_profile,
    save_profile,
)


@click.group(name="profile")
def profile_group() -> None:
    """Manage named profiles of environment variable overrides."""


@profile_group.command("set")
@click.argument("profile_name")
@click.argument("assignments", nargs=-1, required=True)
def set_profile(profile_name: str, assignments: tuple) -> None:
    """Create or update a profile with KEY=VALUE pairs.

    Example: envoy profile set staging DEBUG=0 LOG_LEVEL=warning
    """
    overrides: dict = {}
    for item in assignments:
        if "=" not in item:
            click.echo(f"Invalid assignment (expected KEY=VALUE): {item}", err=True)
            sys.exit(1)
        k, _, v = item.partition("=")
        overrides[k.strip()] = v.strip()
    try:
        path = save_profile(profile_name, overrides)
        click.echo(f"Profile '{profile_name}' saved to {path}.")
    except ProfileError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)


@profile_group.command("show")
@click.argument("profile_name")
def show_profile(profile_name: str) -> None:
    """Display the contents of a profile."""
    try:
        data = load_profile(profile_name)
        click.echo(json.dumps(data, indent=2))
    except ProfileError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)


@profile_group.command("list")
def list_all_profiles() -> None:
    """List all available profiles."""
    names = list_profiles()
    if not names:
        click.echo("No profiles found.")
    for name in names:
        click.echo(name)


@profile_group.command("delete")
@click.argument("profile_name")
def remove_profile(profile_name: str) -> None:
    """Delete a profile."""
    try:
        delete_profile(profile_name)
        click.echo(f"Profile '{profile_name}' deleted.")
    except ProfileError as exc:
        click.echo(str(exc), err=True)
        sys.exit(1)
