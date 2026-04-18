import pytest
from envoy_cli.quota import (
    QuotaError,
    set_quota,
    get_quota,
    remove_quota,
    list_quotas,
    check_quota,
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def test_set_and_get_quota(base):
    set_quota(base, "production", 50)
    assert get_quota(base, "production") == 50


def test_set_creates_file(base):
    from pathlib import Path
    set_quota(base, "staging", 10)
    assert (Path(base) / ".envoy" / "quotas.json").exists()


def test_get_missing_raises(base):
    with pytest.raises(QuotaError, match="No quota set"):
        get_quota(base, "nonexistent")


def test_set_empty_name_raises(base):
    with pytest.raises(QuotaError, match="empty"):
        set_quota(base, "", 10)


def test_set_zero_limit_raises(base):
    with pytest.raises(QuotaError, match="at least 1"):
        set_quota(base, "dev", 0)


def test_set_negative_limit_raises(base):
    with pytest.raises(QuotaError, match="at least 1"):
        set_quota(base, "dev", -5)


def test_remove_quota(base):
    set_quota(base, "dev", 20)
    remove_quota(base, "dev")
    with pytest.raises(QuotaError):
        get_quota(base, "dev")


def test_remove_missing_raises(base):
    with pytest.raises(QuotaError, match="No quota set"):
        remove_quota(base, "ghost")


def test_list_quotas_empty(base):
    assert list_quotas(base) == {}


def test_list_quotas_multiple(base):
    set_quota(base, "dev", 10)
    set_quota(base, "prod", 100)
    result = list_quotas(base)
    assert result == {"dev": 10, "prod": 100}


def test_check_quota_within_limit(base):
    set_quota(base, "dev", 10)
    check_quota(base, "dev", 10)  # should not raise


def test_check_quota_exceeds_limit(base):
    set_quota(base, "dev", 5)
    with pytest.raises(QuotaError, match="Quota exceeded"):
        check_quota(base, "dev", 6)


def test_check_quota_no_quota_set_passes(base):
    check_quota(base, "untracked", 9999)  # no quota set, should pass
