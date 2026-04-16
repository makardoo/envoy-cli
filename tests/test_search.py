import pytest
from click.testing import CliRunner
from envoy_cli.storage import save_env
from envoy_cli.env_file import encrypt_env
from envoy_cli.search import search_key, search_value
from envoy_cli.cli_search import search_group

PASS = "hunter2"


@pytest.fixture()
def store(tmp_path):
    base = str(tmp_path)
    for name, content in [
        ("prod", "DB_HOST=prod.db\nDB_PASS=secret\nPORT=5432\n"),
        ("staging", "DB_HOST=stg.db\nAPI_KEY=abc123\n"),
    ]:
        save_env(base, name, encrypt_env(content, PASS))
    return base


def test_search_key_finds_match(store):
    results = search_key(store, PASS, "DB_HOST")
    names = [r[0] for r in results]
    assert "prod" in names
    assert "staging" in names


def test_search_key_case_insensitive(store):
    results = search_key(store, PASS, "db_host")
    assert len(results) == 2


def test_search_key_limited_to_env(store):
    results = search_key(store, PASS, "DB_HOST", env_name="prod")
    assert all(r[0] == "prod" for r in results)
    assert len(results) == 1


def test_search_key_no_match(store):
    results = search_key(store, PASS, "NONEXISTENT")
    assert results == []


def test_search_value_finds_match(store):
    results = search_value(store, PASS, "secret")
    assert len(results) == 1
    assert results[0][1] == "DB_PASS"


def test_search_wrong_passphrase_skips(store):
    results = search_key(store, "wrongpass", "DB")
    assert results == []


def test_cli_search_key(store):
    runner = CliRunner()
    result = runner.invoke(
        search_group,
        ["key", "API_KEY", "--passphrase", PASS, "--base-dir", store],
    )
    assert result.exit_code == 0
    assert "API_KEY" in result.output


def test_cli_search_value_masks_value(store):
    runner = CliRunner()
    result = runner.invoke(
        search_group,
        ["value", "secret", "--passphrase", PASS, "--base-dir", store],
    )
    assert result.exit_code == 0
    assert "***" in result.output
    assert "secret" not in result.output
