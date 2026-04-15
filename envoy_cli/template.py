"""Template rendering for .env files using variable substitution."""

import re
from typing import Dict, Optional


class TemplateError(Exception):
    """Raised when template rendering fails."""


_VAR_PATTERN = re.compile(r"\$\{([^}]+)\}|\$([A-Za-z_][A-Za-z0-9_]*)")


def render_template(template: str, context: Dict[str, str], strict: bool = True) -> str:
    """Render a template string by substituting ${VAR} or $VAR placeholders.

    Args:
        template: The template string containing variable placeholders.
        context: A dict of variable names to values.
        strict: If True, raise TemplateError for undefined variables.

    Returns:
        The rendered string with all placeholders replaced.
    """
    missing = []

    def replacer(match: re.Match) -> str:
        var_name = match.group(1) or match.group(2)
        if var_name in context:
            return context[var_name]
        if strict:
            missing.append(var_name)
            return match.group(0)
        return match.group(0)

    result = _VAR_PATTERN.sub(replacer, template)

    if strict and missing:
        raise TemplateError(
            f"Undefined variable(s) in template: {', '.join(sorted(set(missing)))}"
        )

    return result


def render_env_template(
    template_content: str,
    context: Dict[str, str],
    strict: bool = True,
) -> str:
    """Render each value in an env-format template string.

    Lines that are comments or blank are passed through unchanged.
    Only the value portion of KEY=VALUE lines is rendered.

    Args:
        template_content: Multi-line env file content.
        context: Variable substitution context.
        strict: If True, raise TemplateError for undefined variables.

    Returns:
        Rendered env file content.
    """
    rendered_lines = []
    for line in template_content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            rendered_lines.append(line)
            continue
        if "=" in stripped:
            key, _, value = stripped.partition("=")
            rendered_value = render_template(value, context, strict=strict)
            rendered_lines.append(f"{key.strip()}={rendered_value}")
        else:
            rendered_lines.append(line)
    return "\n".join(rendered_lines)


def collect_template_vars(template: str) -> list:
    """Return a sorted list of unique variable names referenced in a template."""
    matches = _VAR_PATTERN.findall(template)
    names = {m[0] or m[1] for m in matches}
    return sorted(names)
