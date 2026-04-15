"""CLI commands for validating .env files."""

import click
from envoy_cli.storage import load_env
from envoy_cli.validate import validate_env_content, validate_against_schema


@click.group(name="validate")
def validate_group():
    """Validate .env file contents."""


@validate_group.command(name="check")
@click.argument("env_name")
@click.option("--passphrase", prompt=True, hide_input=True, help="Decryption passphrase.")
@click.option("--require", multiple=True, metavar="KEY", help="Required key(s) that must be present.")
def check_env(env_name: str, passphrase: str, require: tuple):
    """Validate a stored env by name, optionally checking for required keys."""
    try:
        content = load_env(env_name, passphrase)
    except FileNotFoundError:
        click.echo(f"Error: env '{env_name}' not found.", err=True)
        raise SystemExit(1)
    except Exception as exc:
        click.echo(f"Error decrypting env: {exc}", err=True)
        raise SystemExit(1)

    if require:
        result = validate_against_schema(content, list(require))
    else:
        result = validate_env_content(content)

    if not result.issues:
        click.echo(f"✓ '{env_name}' is valid with no issues.")
        return

    for issue in result.issues:
        prefix = "ERROR" if issue.level == "error" else "WARN "
        click.echo(f"  [{prefix}] {issue.message}")

    if result.valid:
        click.echo(f"\n✓ '{env_name}' passed validation with {len(result.issues)} warning(s).")
    else:
        errors = sum(1 for i in result.issues if i.level == "error")
        click.echo(f"\n✗ '{env_name}' failed validation with {errors} error(s).", err=True)
        raise SystemExit(1)


@validate_group.command(name="check-file")
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--require", multiple=True, metavar="KEY", help="Required key(s) that must be present.")
def check_file(filepath: str, require: tuple):
    """Validate a raw (unencrypted) .env file on disk."""
    with open(filepath, "r") as fh:
        content = fh.read()

    if require:
        result = validate_against_schema(content, list(require))
    else:
        result = validate_env_content(content)

    if not result.issues:
        click.echo(f"✓ '{filepath}' is valid with no issues.")
        return

    for issue in result.issues:
        prefix = "ERROR" if issue.level == "error" else "WARN "
        click.echo(f"  [{prefix}] {issue.message}")

    if result.valid:
        click.echo(f"\n✓ '{filepath}' passed with {len(result.issues)} warning(s).")
    else:
        errors = sum(1 for i in result.issues if i.level == "error")
        click.echo(f"\n✗ '{filepath}' failed with {errors} error(s).", err=True)
        raise SystemExit(1)
