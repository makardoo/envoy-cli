"""CLI commands for quota checking."""

from __future__ import annotations

import sys
import click

from envoy_cli.quota_check import check_quota, QuotaExceeded
from envoy_cli.storage import list_envs


@click.group("quota-check")
def quota_check_group() -> None:
    """Check whether environments are within their configured quotas."""


@quota_check_group.command("check")
@click.argument("env_name")
@click.option("--passphrase", envvar="ENVOY_PASSPHRASE", prompt=True, hide_input=True)
@click.option("--base-dir", envvar="ENVOY_BASE_DIR", default=None, hidden=True)
@click.option("--strict", is_flag=True, default=False, help="Exit non-zero if exceeded.")
def check_cmd(env_name: str, passphrase: str, base_dir: str, strict: bool) -> None:
    """Check quota for a single environment."""
    kwargs = {} if base_dir is None else {"base_dir": base_dir}
    try:
        result = check_quota(env_name, passphrase, base_dir=base_dir or "", raise_if_exceeded=False, **{})
        click.echo(str(result))
        if strict and result.exceeded:
            sys.exit(1)
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)


@quota_check_group.command("check-all")
@click.option("--passphrase", envvar="ENVOY_PASSPHRASE", prompt=True, hide_input=True)
@click.option("--base-dir", envvar="ENVOY_BASE_DIR", default=None, hidden=True)
@click.option("--strict", is_flag=True, default=False, help="Exit non-zero if any exceeded.")
def check_all_cmd(passphrase: str, base_dir: str, strict: bool) -> None:
    """Check quotas for all stored environments."""
    try:
        envs = list_envs(base_dir=base_dir or "")
    except Exception as exc:  # noqa: BLE001
        click.echo(f"Error listing envs: {exc}", err=True)
        sys.exit(1)

    if not envs:
        click.echo("No environments found.")
        return

    any_exceeded = False
    for name in sorted(envs):
        try:
            result = check_quota(name, passphrase, base_dir=base_dir or "")
            click.echo(str(result))
            if result.exceeded:
                any_exceeded = True
        except Exception as exc:  # noqa: BLE001
            click.echo(f"{name}: error — {exc}", err=True)

    if strict and any_exceeded:
        sys.exit(1)
