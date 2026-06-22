from asset_list import Asset, AssetList
import pytest
from datetime import datetime

def test_add_asset():
    asset_list = AssetList()
    asset = Asset("Test Asset", "generating", datetime.now(), 1)
    asset_list.add_asset(asset)
    assert len(asset_list.get_assets()) == 1

def test_delete_asset():
    asset_list = AssetList()
    asset = Asset("Test Asset", "generating", datetime.now(), 1)
    asset_list.add_asset(asset)
    asset_list.delete_asset(1)
    assert len(asset_list.get_assets()) == 0

def test_get_asset_list():
    asset_list = AssetList()
    asset1 = Asset("Test Asset 1", "generating", datetime.now(), 1)
    asset2 = Asset("Test Asset 2", "ready", datetime.now(), 2)
    asset_list.add_asset(asset1)
    asset_list.add_asset(asset2)
    asset_list_result = asset_list.get_asset_list()
    assert len(asset_list_result) == 2
    assert asset_list_result[0]["Name"] == "Test Asset 1"
    assert asset_list_result[0]["Status"] == ""
    assert asset_list_result[1]["Name"] == "Test Asset 2"
    assert asset_list_result[1]["Status"] == ""

def test_get_asset_status_icon():
    asset_list = AssetList()
    assert asset_list.get_asset_status_icon("generating") == ""
    assert asset_list.get_asset_status_icon("ready") == ""
    assert asset_list.get_asset_status_icon("expired") == ""
    assert asset_list.get_asset_status_icon("unknown") == ""
