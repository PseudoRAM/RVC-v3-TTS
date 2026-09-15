"""Fetch pinned English VCTK RVC v2 voices and matching retrieval indexes."""
import hashlib
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REVISION = "005c2f948ee9dafd7e3aa7f261b4c3a24beebeef"
BASE = f"https://huggingface.co/Nekochu/RVC-VCTK_Voice-sample/resolve/{REVISION}/"
FILES = {
    "M/p226/rmvpe/Mp226rmvpe.pth": "0a1d55e17cf08c922596710e58a0862cb54c8ea2ab037a5fc1f85c5f08ab4b18",
    "M/p226/rmvpe/added_IVF1161_Flat_nprobe_1_Mp226rmvpe_v2.index": "1325e08293a3a18df46f0d2288296b0788aedb36ebb28962aaec6cce64005341",
    "F/p231/rmvpe/Fp231rmvpe.pth": "12f819e129c6e48779439e491b85593b8819d094f751c3515ea13be6bd8b5a59",
    "F/p231/rmvpe/added_IVF1216_Flat_nprobe_1_Fp231rmvpe_v2.index": "14c3a6fb421ed0c77654bb9ed5778307ff0204d7b047b6bbe37922af42f601ab",
}


def main():
    for remote, expected in FILES.items():
        parts = remote.split("/")
        folder = ROOT / "vendor" / "rvc-v3" / "rvc_models" / ("VCTK" + parts[1][1:])
        folder.mkdir(parents=True, exist_ok=True)
        target = folder / parts[-1]
        if target.exists() and hashlib.sha256(target.read_bytes()).hexdigest() == expected:
            print(f"Verified {target.name}")
            continue
        temporary = target.with_suffix(target.suffix + ".download")
        try:
            with urllib.request.urlopen(BASE + remote, timeout=60) as response, temporary.open("wb") as output:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    output.write(chunk)
            if hashlib.sha256(temporary.read_bytes()).hexdigest() != expected:
                raise ValueError(f"Checksum mismatch: {remote}")
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
        print(f"Downloaded and verified {target.name}")
    print("Credits and terms: examples/README.md and examples/licenses/")


if __name__ == "__main__":
    main()
