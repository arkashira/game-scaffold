from dataclasses import dataclass
from datetime import datetime
from typing import List

@dataclass
class Asset:
    name: str
    status: str
    created_at: datetime
    id: int

class AssetList:
    def __init__(self):
        self.assets = []

    def add_asset(self, asset: Asset):
        self.assets.append(asset)

    def delete_asset(self, asset_id: int):
        self.assets = [asset for asset in self.assets if asset.id != asset_id]

    def get_assets(self) -> List[Asset]:
        return self.assets

    def get_asset_status_icon(self, status: str) -> str:
        if status == "generating":
            return ""
        elif status == "ready":
            return ""
        elif status == "expired":
            return ""
        else:
            return ""

    def get_asset_list(self) -> List[dict]:
        assets = self.get_assets()
        asset_list = []
        for asset in assets:
            asset_dict = {
                "Name": asset.name,
                "Status": self.get_asset_status_icon(asset.status),
                "Created At": asset.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "Actions": f"Delete {asset.id}"
            }
            asset_list.append(asset_dict)
        return asset_list
