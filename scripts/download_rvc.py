"""Download shared HuBERT/RMVPE assets, checking upstream SHA256 hashes."""
import hashlib
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
ASSETS = {
    "hubert_base.pt": "f54b40fd2802423a5643779c4861af1e9ee9c1564dc9d32f54f20b5ffba7db96",
    "rmvpe.pt": "6d62215f4306e3ca278246188607209f09af3dc77ed4232efdd069798c4ec193",
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    folder = ROOT / "vendor" / "rvc-v3" / "rvc_models"
    folder.mkdir(parents=True, exist_ok=True)
    for name, expected in ASSETS.items():
        target = folder / name
        if target.is_file() and sha256(target) == expected:
            print(f"Verified existing {name}")
            continue
        temporary = target.with_suffix(".download")
        try:
            url = "https://huggingface.co/lj1995/VoiceConversionWebUI/resolve/main/" + name
            with urllib.request.urlopen(url, timeout=60) as response, temporary.open("wb") as output:
                size = 0
                for block in iter(lambda: response.read(1024 * 1024), b""):
                    size += len(block)
                    if size > 512 * 1024**2:
                        raise ValueError("Shared asset exceeds expected size limit")
                    output.write(block)
            if sha256(temporary) != expected:
                raise ValueError(f"Checksum mismatch for {name}; existing model preserved")
            temporary.replace(target)
        finally:
            if temporary.exists():
                temporary.unlink()
        print(f"Downloaded and verified {name}")


if __name__ == "__main__":
    main()

