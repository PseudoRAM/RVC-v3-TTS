"""Verify the exact expressive weights tested in the local release image."""
import hashlib
from pathlib import Path

root = Path(__file__).resolve().parents[1] / 'models' / 'qwen3-tts-customvoice'
expected = {
    'model.safetensors': '38b1d5971bdbd982b561cccec982669a53b0537c3cf5e9bd4778ed07bb2f5137',
    'speech_tokenizer/model.safetensors': '836b7b357f5ea43e889936a3709af68dfe3751881acefe4ecf0dbd30ba571258',
}
for name, digest in expected.items():
    with (root / name).open('rb') as source:
        actual = hashlib.file_digest(source, 'sha256').hexdigest()
    if actual != digest:
        raise ValueError('Expressive weight checksum mismatch: ' + name)
    print('Verified', name, actual)
