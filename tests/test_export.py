"""Tests for envoy_cli.export module."""

import json
import pytest

from envoy_cli.export import (
    parse_env_dict,
    export_shell,
    export_docker,
    export_json,
    export_env,
    SUPPORTED_FORMATS,
)

SAMPLE_CONTENT = """
# database settings
DB_HOST=localhost
DB_PORT=5432
DB_PASSWORD=s3cr3t

APP_NAME=my app
"""


def test_parse_env_dict_basic():
    result = parse_env_dict(SAMPLE_CONTENT)
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"
    assert result["DB_PASSWORD"] == "s3cr3t"
    assert result["APP_NAME"] == "my app"


def test_parse_env_dict_ignores_comments_and_blanks():
    result = parse_env_dict(SAMPLE_CONTENT)
    assert all(not k.startswith("#") for k in result)
    assert len(result) == 4


def test_parse_env_dict_value_with_equals():
    content = "TOKEN=abc=def=ghi\n"
    result = parse_env_dict(content)
    assert result["TOKEN"] == "abc=def=ghi"


def test_export_shell_format():
    output = export_env(SAMPLE_CONTENT, "shell")
    assert 'export DB_HOST="localhost"' in output
    assert 'export DB_PASSWORD="s3cr3t"' in output
    assert output.endswith("\n")


def test_export_shell_escapes_double_quotes():
    content = 'MSG=say "hello"\n'
    output = export_shell({"MSG": 'say "hello"'})
    assert 'export MSG="say \\"hello\\""' in output


def test_export_docker_format():
    output = export_env(SAMPLE_CONTENT, "docker")
    assert "DB_HOST=localhost" in output
    assert "DB_PORT=5432" in output
    assert output.endswith("\n")


def test_export_docker_no_quotes():
    output = export_docker({"KEY": "value"})
    assert '"' not in output


def test_export_json_format():
    output = export_env(SAMPLE_CONTENT, "json")
    data = json.loads(output)
    assert data["DB_HOST"] == "localhost"
    assert data["APP_NAME"] == "my app"


def test_export_json_is_sorted():
    output = export_json({"Z": "1", "A": "2", "M": "3"})
    data = json.loads(output)
    assert list(data.keys()) == sorted(data.keys())


def test_export_env_unsupported_format_raises():
    with pytest.raises(ValueError, match="Unsupported format"):
        export_env(SAMPLE_CONTENT, "xml")


def test_supported_formats_constant():
    assert "shell" in SUPPORTED_FORMATS
    assert "docker" in SUPPORTED_FORMATS
    assert "json" in SUPPORTED_FORMATS


def test_export_empty_content_returns_empty():
    for fmt in SUPPORTED_FORMATS:
        output = export_env("", fmt)
        if fmt == "json":
            assert json.loads(output) == {}
        else:
            assert output == ""
