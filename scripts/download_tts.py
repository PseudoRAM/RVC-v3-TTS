"""Download the fixed Kokoro ONNX v1.0 release into this project."""
from pathlib import Path
import hashlib
import json
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/'
HASHES = {
    'kokoro-v1.0.onnx': 'beb0d1848dee9a49da392cc3df26958d46cfa35d321edf434f52949153f0df3a',
    'voices-v1.0.bin': 'bca610b8308e8d99f32e6fe4197e7ec01679264efed0cac9140fe9c29f1fbf7d',
}

def main():
    folder = ROOT / 'models'
    folder.mkdir(exist_ok=True)
    manifest = {}
    for name in ('kokoro-v1.0.onnx', 'voices-v1.0.bin'):
        target = folder / name
        if not target.exists():
            temporary = target.with_suffix('.download')
            with urllib.request.urlopen(BASE + name, timeout=120) as source, temporary.open('wb') as out:
                while block := source.read(1024 * 1024):
                    out.write(block)
            if hashlib.sha256(temporary.read_bytes()).hexdigest() != HASHES[name]:
                temporary.unlink()
                raise ValueError(f'Checksum mismatch: {name}')
            temporary.replace(target)
        digest = hashlib.sha256(target.read_bytes()).hexdigest()
        if digest != HASHES[name]:
            raise ValueError(f'Existing {name} failed checksum; remove it and retry')
        manifest[name] = {'url': BASE + name, 'sha256': digest, 'bytes': target.stat().st_size}
        print(name, digest, flush=True)
    (folder / 'manifest.json').write_text(json.dumps(manifest, indent=2))

if __name__ == '__main__':
    main()
