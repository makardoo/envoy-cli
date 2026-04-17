import pytest
from pathlib import Path
from envoy_cli.backup import (
    BackupError, create_backup, list_backups, restore_backup, delete_backup
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_create_backup_returns_path(base):
    path = create_backup(base, "prod", "before-deploy", "KEY=val")
    assert Path(path).exists()


def test_create_backup_file_contains_json(base):
    import json
    path = create_backup(base, "prod", "v1", "KEY=val")
    data = json.loads(Path(path).read_text())
    assert data["env"] == "prod"
    assert data["label"] == "v1"
    assert data["content"] == "KEY=val"
    assert "created_at" in data


def test_create_backup_duplicate_raises(base):
    create_backup(base, "prod", "v1", "A=1")
    with pytest.raises(BackupError, match="already exists"):
        create_backup(base, "prod", "v1", "A=2")


def test_create_backup_empty_name_raises(base):
    with pytest.raises(BackupError, match="name"):
        create_backup(base, "", "v1", "A=1")


def test_create_backup_empty_label_raises(base):
    with pytest.raises(BackupError, match="label"):
        create_backup(base, "prod", "", "A=1")


def test_list_backups_returns_all(base):
    create_backup(base, "prod", "v1", "A=1")
    create_backup(base, "prod", "v2", "A=2")
    results = list_backups(base, "prod")
    assert len(results) == 2
    labels = {r["label"] for r in results}
    assert labels == {"v1", "v2"}


def test_list_backups_empty(base):
    assert list_backups(base, "staging") == []


def test_list_backups_scoped_to_env(base):
    create_backup(base, "prod", "v1", "A=1")
    create_backup(base, "staging", "v1", "B=2")
    assert len(list_backups(base, "prod")) == 1
    assert len(list_backups(base, "staging")) == 1


def test_restore_backup_returns_content(base):
    create_backup(base, "prod", "v1", "KEY=secret")
    content = restore_backup(base, "prod", "v1")
    assert content == "KEY=secret"


def test_restore_missing_raises(base):
    with pytest.raises(BackupError, match="no backup"):
        restore_backup(base, "prod", "ghost")


def test_delete_backup_removes_file(base):
    create_backup(base, "prod", "v1", "A=1")
    delete_backup(base, "prod", "v1")
    assert list_backups(base, "prod") == []


def test_delete_missing_raises(base):
    with pytest.raises(BackupError, match="no backup"):
        delete_backup(base, "prod", "ghost")
