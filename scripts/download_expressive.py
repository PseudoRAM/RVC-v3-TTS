"""Download the pinned official CustomVoice model for offline emotion control."""
from pathlib import Path
import sys
import json
from huggingface_hub import snapshot_download

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from emotion import MODEL_ID, MODEL_REVISION, MODEL_FOLDER

if __name__ == '__main__':
    folder = ROOT / 'models' / MODEL_FOLDER
    snapshot_download(MODEL_ID, revision=MODEL_REVISION, local_dir=str(folder),
                      allow_patterns=['*.json', '*.safetensors', '*.txt', '*.model'], max_workers=4)
    (folder / 'download-manifest.json').write_text(json.dumps(
        {'model_id': MODEL_ID, 'revision': MODEL_REVISION}, indent=2))
    print(folder)
