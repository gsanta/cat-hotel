import json
import requests
import threading
from typing import List, Dict, Any, Optional
from django.conf import settings


class ManifestClient:
    """
    A client for fetching and parsing frontend asset manifest files.
    Thread-safe implementation with optional caching.
    """
    
    def __init__(self, manifest_host: str):
        self.manifest_host = manifest_host
        self._manifest: Optional[Dict[str, Any]] = None
        self._lock = threading.Lock()
    
    def fetch_manifest(self) -> None:
        """
        Fetches the manifest from the configured host.
        TODO: Add memoization for production use.
        """
        with self._lock:
            # TODO: memoize manifest in production
            # if self._manifest is not None:
            #     return
            
            url = f"{self.manifest_host}/version-dev/manifest.json"
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                self._manifest = response.json()
            except (requests.RequestException, json.JSONDecodeError) as e:
                self._manifest = None
                raise RuntimeError(f"Failed to fetch manifest from {url}: {e}")
    
    def get_js(self, entry: str) -> List[str]:
        """
        Returns a list of JavaScript file paths for the given entry point.
        
        Args:
            entry: The entry point name (e.g., 'main', 'admin')
        
        Returns:
            List of JavaScript file paths, empty list if not found
        """
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
        """
        Returns a list of CSS file paths for the given entry point.
        
        Args:
            entry: The entry point name (e.g., 'main', 'admin')
        
        Returns:
            List of CSS file paths, empty list if not found
        """
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


# Global instance - configure in settings
_manifest_client: Optional[ManifestClient] = None


def get_manifest_client() -> ManifestClient:
    """
    Returns a singleton instance of ManifestClient configured from Django settings.
    """
    global _manifest_client
    
    if _manifest_client is None:
        manifest_host = getattr(settings, 'MANIFEST_HOST', 'http://localhost:3000')
        _manifest_client = ManifestClient(manifest_host)
    
    return _manifest_client


def get_js_files(entry: str) -> List[str]:
    """
    Convenience function to get JavaScript files for an entry point.
    """
    return get_manifest_client().get_js(entry)


def get_css_files(entry: str) -> List[str]:
    """
    Convenience function to get CSS files for an entry point.
    """
    return get_manifest_client().get_css(entry)
