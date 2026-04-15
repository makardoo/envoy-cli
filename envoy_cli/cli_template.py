"""CLI commands for rendering .env templates."""

import sys
from pathlib import Path

import click

from .template import TemplateError, collect_template_vars, render_env_template
from .storage import load_env
from .env_file import decrypt_env


@click.group("template")
def template_group() -> None:
    """Render .env templates with variable substitution."""


@template_group.command("render")
@click.argument("template_file", type=click.Path(exists=True))
@click.option("--env-name", "-e", default=None, help="Stored env name to use as context.")
@click.option("--passphrase", "-p", default=None, envvar="ENVOY_PASSPHRASE", help="Passphrase to decrypt stored env.")
@click.option("--var", "-v", multiple=True, metavar="KEY=VALUE", help="Extra variables (can be repeated).")
@click.option("--strict/--no-strict", default=True, show_default=True, help="Fail on undefined variables.")
@click.option("--output", "-o", default=None, type=click.Path(), help="Write output to file instead of stdout.")
def render(template_file, env_name, passphrase, var, strict, output):
    """Render TEMPLATE_FILE substituting variables from a stored env and/or --var flags."""
    context = {}

    if env_name:
        if not passphrase:
            passphrase = click.prompt("Passphrase", hide_input=True)
        try:
            raw = load_env(env_name)
            decrypted = decrypt_env(raw, passphrase)
        except FileNotFoundError:
            click.echo(f"Error: env '{env_name}' not found.", err=True)
            sys.exit(1)
        except Exception as exc:
            click.echo(f"Error decrypting env: {exc}", err=True)
            sys.exit(1)
        for line in decrypted.splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            context[k.strip()] = v

    for item in var:
        if "=" not in item:
            click.echo(f"Error: --var must be KEY=VALUE, got: {item!r}", err=True)
            sys.exit(1)
        k, _, v = item.partition("=")
        context[k.strip()] = v

    template_content = Path(template_file).read_text()

    try:
        result = render_env_template(template_content, context, strict=strict)
    except TemplateError as exc:
        click.echo(f"Template error: {exc}", err=True)
        sys.exit(1)

    if output:
        Path(output).write_text(result)
        click.echo(f"Written to {output}")
    else:
        click.echo(result)


@template_group.command("vars")
@click.argument("template_file", type=click.Path(exists=True))
def list_vars(template_file):
    """List all variable placeholders found in TEMPLATE_FILE."""
    content = Path(template_file).read_text()
    names = collect_template_vars(content)
    if not names:
        click.echo("No variables found.")
    else:
        for name in names:
            click.echo(name)
