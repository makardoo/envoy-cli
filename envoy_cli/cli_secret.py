"""CLI commands for secret scanning."""

from __future__ import annotations

import sys
import click

from envoy_cli.secret import scan_env, scan_content, SecretError
from envoy_cli.storage import list_envs


@click.group(name="secret")
def secret_group():
    """Scan env files for exposed secrets."""


@secret_group.command(name="scan")
@click.argument("env_name")
@click.option("--passphrase", "-p", required=True, help="Decryption passphrase.")
@click.option("--show-values", is_flag=True, default=False, help="Show masked secret values.")
def scan_cmd(env_name: str, passphrase: str, show_values: bool):
    """Scan a stored env file for potential secrets."""
    try:
        result = scan_env(env_name, passphrase)
    except SecretError as exc:
        click.echo(f"Error: {exc}", err=True)
        sys.exit(1)
    except Exception:
        click.echo("Error: decryption failed — wrong passphrase?", err=True)
        sys.exit(1)

    if result.clean:
        click.echo(f"✓ No secrets detected in '{env_name}'.")
        return

    click.echo(f"⚠ {len(result.findings)} potential secret(s) found in '{env_name}':\n")
    for f in result.findings:
        val_display = f" = {f.masked_value()}" if show_values else ""
        click.echo(f"  line {f.line:>3}  [{f.rule}]  {f.key}{val_display}")
    sys.exit(1)


@secret_group.command(name="scan-all")
@click.option("--passphrase", "-p", required=True, help="Decryption passphrase.")
@click.option("--show-values", is_flag=True, default=False)
def scan_all_cmd(passphrase: str, show_values: bool):
    """Scan all stored env files for potential secrets."""
    envs = list_envs()
    if not envs:
        click.echo("No env files found.")
        return

    found_any = False
    for env_name in sorted(envs):
        try:
            result = scan_env(env_name, passphrase)
        except Exception:
            click.echo(f"  {env_name}: skipped (error)")
            continue
        if not result.clean:
            found_any = True
            click.echo(f"⚠ {env_name}: {len(result.findings)} finding(s)")
            for f in result.findings:
                val_display = f" = {f.masked_value()}" if show_values else ""
                click.echo(f"    line {f.line:>3}  [{f.rule}]  {f.key}{val_display}")
        else:
            click.echo(f"✓ {env_name}: clean")

    if found_any:
        sys.exit(1)
