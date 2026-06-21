import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional

@dataclass
class Asset:
    name: str
    type: str
    creation_time: datetime.datetime = field(default_factory=datetime.datetime.utcnow)
    thumbnail: str = ""
    full_preview: str = ""

    def to_dict(self) -> Dict[str, str]:
        """Return a dictionary representation suitable for the dashboard."""
        return {
            "name": self.name,
            "type": self.type,
            "creation_time": self.creation_time.isoformat() + "Z",
            "thumbnail": self.thumbnail,
        }

    def detail_dict(self) -> Dict[str, str]:
        """Return a dictionary with full preview and metadata."""
        d = self.to_dict()
        d["full_preview"] = self.full_preview
        return d


class AssetManager:
    """Manages a collection of temporary game assets."""

    def __init__(self) -> None:
        self._assets: Dict[str, Asset] = {}
        self._needs_refresh: bool = False

    def add_asset(
        self,
        name: str,
        type: str,
        creation_time: Optional[datetime.datetime] = None,
        thumbnail: Optional[str] = None,
        full_preview: Optional[str] = None,
    ) -> None:
        """Add a new asset. Raises ValueError if name already exists."""
        if name in self._assets:
            raise ValueError(f"Asset with name '{name}' already exists.")
        if creation_time is None:
            creation_time = datetime.datetime.utcnow()
        if thumbnail is None:
            thumbnail = f"[thumb:{name}]"
        if full_preview is None:
            full_preview = f"[full:{name}]"
        asset = Asset(
            name=name,
            type=type,
            creation_time=creation_time,
            thumbnail=thumbnail,
            full_preview=full_preview,
        )
        self._assets[name] = asset
        self._needs_refresh = True

    def list_assets(self) -> List[Dict[str, str]]:
        """Return a list of asset summaries for the dashboard."""
        if self._needs_refresh:
            self.refresh()
        return [asset.to_dict() for asset in sorted(self._assets.values(), key=lambda a: a.creation_time)]

    def get_asset_detail(self, name: str) -> Dict[str, str]:
        """Return full details of a specific asset."""
        if name not in self._assets:
            raise KeyError(f"Asset '{name}' not found.")
        return self._assets[name].detail_dict()

    def refresh(self) -> None:
        """Refresh internal state. For this in-memory implementation, it simply clears the flag."""
        self._needs_refresh = False
