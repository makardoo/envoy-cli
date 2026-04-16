import pytest
from envoy_cli.schedule import (
    ScheduleError, SyncSchedule, add_schedule, remove_schedule,
    list_schedules, get_schedule, toggle_schedule,
)


@pytest.fixture
def base(tmp_path):
    return str(tmp_path)


def _make(env_name="production", cron="0 * * * *", direction="push", profile="default"):
    return SyncSchedule(env_name=env_name, cron=cron, direction=direction, profile=profile)


def test_add_and_list(base):
    add_schedule(base, _make())
    schedules = list_schedules(base)
    assert len(schedules) == 1
    assert schedules[0].env_name == "production"


def test_add_creates_file(base, tmp_path):
    add_schedule(base, _make())
    assert (tmp_path / "schedules.json").exists()


def test_add_duplicate_raises(base):
    add_schedule(base, _make())
    with pytest.raises(ScheduleError, match="already exists"):
        add_schedule(base, _make())


def test_add_same_env_different_direction(base):
    add_schedule(base, _make(direction="push"))
    add_schedule(base, _make(direction="pull"))
    assert len(list_schedules(base)) == 2


def test_remove_schedule(base):
    add_schedule(base, _make())
    remove_schedule(base, "production", "push")
    assert list_schedules(base) == []


def test_remove_missing_raises(base):
    with pytest.raises(ScheduleError, match="No schedule found"):
        remove_schedule(base, "ghost", "push")


def test_get_schedule(base):
    add_schedule(base, _make(cron="5 4 * * *"))
    s = get_schedule(base, "production", "push")
    assert s.cron == "5 4 * * *"


def test_get_missing_raises(base):
    with pytest.raises(ScheduleError):
        get_schedule(base, "missing", "pull")


def test_toggle_disable(base):
    add_schedule(base, _make())
    toggle_schedule(base, "production", "push", enabled=False)
    s = get_schedule(base, "production", "push")
    assert s.enabled is False


def test_toggle_enable(base):
    add_schedule(base, _make())
    toggle_schedule(base, "production", "push", enabled=False)
    toggle_schedule(base, "production", "push", enabled=True)
    s = get_schedule(base, "production", "push")
    assert s.enabled is True


def test_toggle_missing_raises(base):
    with pytest.raises(ScheduleError):
        toggle_schedule(base, "nope", "push", enabled=True)


def test_list_empty(base):
    assert list_schedules(base) == []


def test_schedule_default_enabled(base):
    add_schedule(base, _make())
    s = get_schedule(base, "production", "push")
    assert s.enabled is True
