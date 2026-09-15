"""Bounded caches. Call under the service lock (one request per worker)."""
from collections import OrderedDict
import hashlib
import os
from pathlib import Path
import shutil
import tempfile
import time
import urllib.parse
import urllib.request
import zipfile


class ModelCache:
    def __init__(self, capacity=1):
        if capacity < 1:
            raise ValueError("Model cache capacity must be positive")
        self.capacity = capacity
        self.items = OrderedDict()

    def get(self, key, loader):
        if key in self.items:
            self.items.move_to_end(key)
            return self.items[key], True
        while len(self.items) >= self.capacity:
            self.items.popitem(last=False)
        value = loader()
        self.items[key] = value
        return value, False


def model_files(directory):
    directory = Path(directory)
    if not directory.is_dir():
        raise FileNotFoundError("Voice directory is missing. Provision its checkpoint or supply a custom model URL.")
    voices = sorted(directory.rglob("*.pth"))
    indexes = sorted(directory.rglob("*.index"))
    if len(voices) != 1:
        raise ValueError("A voice directory must contain exactly one .pth checkpoint")
    if len(indexes) > 1:
        raise ValueError("A voice directory must contain at most one .index file")
    return voices[0], indexes[0] if indexes else None


class DownloadCache:
    def __init__(self, root, capacity=4, max_bytes=1024**3, ttl=86400):
        if min(capacity, max_bytes, ttl) <= 0:
            raise ValueError("Download cache limits must be positive")
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.capacity, self.max_bytes, self.ttl = capacity, max_bytes, ttl

    def get(self, url, refresh=False):
        if urllib.parse.urlsplit(url).scheme not in ("https", "http"):
            raise ValueError("Custom model URL must use HTTP or HTTPS")
        # Include query parameters; never log signed URLs or store them on disk.
        key = hashlib.sha256(url.encode()).hexdigest()
        target = self.root / key
        marker = target / ".complete"
        if marker.is_file() and not refresh and time.time() - marker.stat().st_mtime < self.ttl:
            model_files(target)
            os.utime(target, None)
            return target, True
        with tempfile.TemporaryDirectory(prefix="download-", dir=self.root) as temp:
            temp = Path(temp)
            archive = temp / "model.zip"
            with urllib.request.urlopen(url, timeout=60) as response, archive.open("wb") as output:
                if urllib.parse.urlsplit(response.geturl()).scheme not in ("http", "https"):
                    raise ValueError("Unsupported download redirect")
                total = 0
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > self.max_bytes:
                        raise ValueError("Model archive exceeds download limit")
                    output.write(chunk)
            staged = temp / "ready"
            staged.mkdir()
            with zipfile.ZipFile(archive) as bundle:
                members = [m for m in bundle.infolist() if not m.is_dir() and Path(m.filename).suffix.lower() in (".pth", ".index")]
                if sum(m.file_size for m in members) > self.max_bytes:
                    raise ValueError("Extracted model exceeds size limit")
                names = set()
                for member in members:
                    # Flatten names rather than trusting archive directory paths.
                    name = Path(member.filename.replace("\\", "/")).name
                    if name.casefold() in names:
                        raise ValueError("Duplicate model filename in archive")
                    names.add(name.casefold())
                    with bundle.open(member) as source, (staged / name).open("wb") as output:
                        shutil.copyfileobj(source, output)
            model_files(staged)
            (staged / ".complete").touch()
            # The previous usable entry survives failed downloads and validation.
            if target.exists():
                shutil.rmtree(target)
            staged.rename(target)
        entries = sorted((p for p in self.root.iterdir() if p.is_dir() and (p / ".complete").is_file()), key=lambda p: p.stat().st_mtime)
        for entry in [p for p in entries if p != target][:max(0, len(entries) - self.capacity)]:
            shutil.rmtree(entry)
        return target, False
