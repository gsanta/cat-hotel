import json
import requests
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional
from django.conf import settings


class ManifestClient:
    """
    A client for fetching and parsing frontend asset manifest files.
    In development: fetches from the webpack dev server on every request.
    In production: reads from disk once and caches permanently.
    """

    def __init__(self, manifest_host: str, manifest_path: Optional[Path] = None):
        self.manifest_host = manifest_host
        self.manifest_path = manifest_path
        self._manifest: Optional[Dict[str, Any]] = None
        self._lock = threading.Lock()

    def fetch_manifest(self) -> None:
        with self._lock:
            if self.manifest_path is not None:
                # Production: read from disk, cache permanently
                if self._manifest is not None:
                    return
                try:
                    self._manifest = json.loads(self.manifest_path.read_text())
                except (OSError, json.JSONDecodeError) as e:
                    self._manifest = None
                    raise RuntimeError(f"Failed to read manifest from {self.manifest_path}: {e}")
            else:
                # Development: fetch from webpack dev server every time
                url = f"{self.manifest_host}/version-dev/manifest.json"
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    self._manifest = response.json()
                except (requests.RequestException, json.JSONDecodeError) as e:
                    self._manifest = None
                    raise RuntimeError(f"Failed to fetch manifest from {url}: {e}")

    def get_js(self, entry: str) -> List[str]:
        try:
            self.fetch_manifest()
            if not self._manifest:
                return []
            entrypoints = self._manifest.get("entrypoints", {})
            if not isinstance(entrypoints, dict):
                return []
            entry_node = entrypoints.get(entry, {})
            if not isinstance(entry_node, dict):
                return []
            assets = entry_node.get("assets", {})
            if not isinstance(assets, dict):
                return []
            js_files = assets.get("js", [])
            if not isinstance(js_files, list):
                return []
            return [f for f in js_files if isinstance(f, str)]
        except Exception:
            return []

    def get_css(self, entry: str) -> List[str]:
        try:
            self.fetch_manifest()
            if not self._manifest:
                return []
            entrypoints = self._manifest.get("entrypoints", {})
            if not isinstance(entrypoints, dict):
                return []
            entry_node = entrypoints.get(entry, {})
            if not isinstance(entry_node, dict):
                return []
            assets = entry_node.get("assets", {})
            if not isinstance(assets, dict):
                return []
            css_files = assets.get("css", [])
            if not isinstance(css_files, list):
                return []
            return [f for f in css_files if isinstance(f, str)]
        except Exception:
            return []


_manifest_client: Optional[ManifestClient] = None


def get_manifest_client() -> ManifestClient:
    global _manifest_client

    if _manifest_client is None:
        manifest_host = getattr(settings, 'MANIFEST_HOST', 'http://localhost:3000')
        manifest_path = getattr(settings, 'MANIFEST_PATH', None)
        _manifest_client = ManifestClient(manifest_host, manifest_path)

    return _manifest_client


def get_js_files(entry: str) -> List[str]:
    return get_manifest_client().get_js(entry)


def get_css_files(entry: str) -> List[str]:
    return get_manifest_client().get_css(entry)
