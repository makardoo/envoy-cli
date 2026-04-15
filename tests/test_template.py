"""Tests for envoy_cli.template module."""

import pytest

from envoy_cli.template import (
    TemplateError,
    collect_template_vars,
    render_env_template,
    render_template,
)


# ---------------------------------------------------------------------------
# render_template
# ---------------------------------------------------------------------------

def test_render_template_dollar_brace():
    result = render_template("Hello ${NAME}!", {"NAME": "World"})
    assert result == "Hello World!"


def test_render_template_bare_dollar():
    result = render_template("prefix_$VAR_suffix", {"VAR": "x"})
    assert result == "prefix_x_suffix"


def test_render_template_multiple_vars():
    result = render_template("${A}-${B}", {"A": "foo", "B": "bar"})
    assert result == "foo-bar"


def test_render_template_strict_raises_on_missing():
    with pytest.raises(TemplateError, match="MISSING"):
        render_template("${MISSING}", {}, strict=True)


def test_render_template_non_strict_leaves_placeholder():
    result = render_template("${MISSING}", {}, strict=False)
    assert result == "${MISSING}"


def test_render_template_no_placeholders():
    result = render_template("plain text", {})
    assert result == "plain text"


def test_render_template_multiple_missing_vars_all_reported():
    with pytest.raises(TemplateError) as exc_info:
        render_template("${A} ${B} ${A}", {}, strict=True)
    msg = str(exc_info.value)
    assert "A" in msg
    assert "B" in msg


# ---------------------------------------------------------------------------
# render_env_template
# ---------------------------------------------------------------------------

def test_render_env_template_substitutes_values():
    template = "DB_HOST=${HOST}\nDB_PORT=${PORT}"
    result = render_env_template(template, {"HOST": "localhost", "PORT": "5432"})
    assert "DB_HOST=localhost" in result
    assert "DB_PORT=5432" in result


def test_render_env_template_preserves_comments_and_blanks():
    template = "# comment\n\nKEY=${VAL}"
    result = render_env_template(template, {"VAL": "hello"})
    assert "# comment" in result
    assert "KEY=hello" in result


def test_render_env_template_strict_raises():
    with pytest.raises(TemplateError):
        render_env_template("KEY=${UNDEFINED}", {}, strict=True)


def test_render_env_template_non_strict_leaves_placeholder():
    result = render_env_template("KEY=${UNDEFINED}", {}, strict=False)
    assert "KEY=${UNDEFINED}" in result


def test_render_env_template_value_with_equals():
    template = "TOKEN=${SECRET}"
    result = render_env_template(template, {"SECRET": "abc=def"})
    assert "TOKEN=abc=def" in result


# ---------------------------------------------------------------------------
# collect_template_vars
# ---------------------------------------------------------------------------

def test_collect_template_vars_finds_brace_style():
    names = collect_template_vars("${FOO} and ${BAR}")
    assert names == ["BAR", "FOO"]


def test_collect_template_vars_finds_bare_style():
    names = collect_template_vars("$FOO and $BAR")
    assert names == ["BAR", "FOO"]


def test_collect_template_vars_deduplicates():
    names = collect_template_vars("${X} ${X} ${X}")
    assert names == ["X"]


def test_collect_template_vars_empty():
    names = collect_template_vars("no vars here")
    assert names == []
