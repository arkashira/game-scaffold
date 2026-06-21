import datetime
import pytest

from asset_manager import AssetManager


@pytest.fixture
def manager() -> AssetManager:
    return AssetManager()


def test_empty_list(manager: AssetManager):
    """Dashboard should show no assets initially."""
    assert manager.list_assets() == []


def test_add_and_list(manager: AssetManager):
    """Adding assets should reflect in the dashboard list."""
    manager.add_asset(name="hero_sprite", type="sprite")
    manager.add_asset(name="background_music", type="audio")
    assets = manager.list_assets()
    assert len(assets) == 2
    names = {a["name"] for a in assets}
    assert names == {"hero_sprite", "background_music"}
    for asset in assets:
        assert "thumbnail" in asset
        assert asset["thumbnail"].startswith("[thumb:")


def test_get_detail(manager: AssetManager):
    """Clicking an asset should provide full preview and metadata."""
    manager.add_asset(name="level_map", type="map")
    detail = manager.get_asset_detail("level_map")
    assert detail["name"] == "level_map"
    assert detail["type"] == "map"
    assert detail["full_preview"] == "[full:level_map]"
    assert "creation_time" in detail
    # Validate ISO format
    datetime.datetime.fromisoformat(detail["creation_time"].rstrip("Z"))


def test_duplicate_asset(manager: AssetManager):
    """Adding an asset with an existing name should raise ValueError."""
    manager.add_asset(name="duplicate", type="sprite")
    with pytest.raises(ValueError) as excinfo:
        manager.add_asset(name="duplicate", type="audio")
    assert "already exists" in str(excinfo.value)


def test_missing_asset(manager: AssetManager):
    """Requesting a non-existent asset should raise KeyError."""
    with pytest.raises(KeyError) as excinfo:
        manager.get_asset_detail("nonexistent")
    assert "not found" in str(excinfo.value)


def test_auto_refresh(manager: AssetManager):
    """Dashboard should automatically include new assets after addition."""
    manager.add_asset(name="first_asset", type="sprite")
    assert len(manager.list_assets()) == 1
    manager.add_asset(name="second_asset", type="audio")
    # After adding, list_assets should reflect both
    assets = manager.list_assets()
    assert len(assets) == 2
    names = {a["name"] for a in assets}
    assert names == {"first_asset", "second_asset"}


def test_creation_time_order(manager: AssetManager):
    """Assets should be sorted by creation time."""
    now = datetime.datetime.utcnow()
    earlier = now - datetime.timedelta(seconds=10)
    manager.add_asset(name="old_asset", type="sprite", creation_time=earlier)
    manager.add_asset(name="new_asset", type="audio", creation_time=now)
    assets = manager.list_assets()
    assert assets[0]["name"] == "old_asset"
    assert assets[1]["name"] == "new_asset"
